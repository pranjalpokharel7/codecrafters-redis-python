import socket  # noqa: F401
import threading

from app.exec import NAME_TO_COMMANDS_MAP
from app.exec.base import ExecutionContext
from app.storage.in_memory_db import InMemoryDB as Storage
from app.types.resp import Array, Nil, resp_type_from_bytes

MAX_BUF_SIZE = 512


def handle_connection(client_socket: socket.socket, ctx: ExecutionContext):
    while True:
        chunk = client_socket.recv(MAX_BUF_SIZE)
        if not chunk:  # empty buffer means client has disconnected
            break

        # default response is nil (null bulk string)
        response = bytes(Nil)

        parsed_input, _ = resp_type_from_bytes(chunk)

        # TODO: refactor this into a different function in the next stage
        if isinstance(parsed_input, Array):
            array = parsed_input.value
            command_name = array[0].value
            subcommand_name = array[1].value if len(array) > 1 else b""

            # longest prefix match for commands with compound names
            if cmd := NAME_TO_COMMANDS_MAP.get(command_name + b" " + subcommand_name):
                # use raw values (bytes) as arguments
                command = cmd([element.value for element in array[2:]])

            # shorter prefix is a single command name with no subcommand which we map next
            elif cmd := NAME_TO_COMMANDS_MAP.get(command_name):
                command = cmd([element.value for element in array[1:]])

            else:
                raise Exception("unrecognized command")

            response = command.exec(ctx)

        client_socket.sendall(response)


def main():
    print("Logs from your program will appear here!")
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    storage = Storage()
    execution_context = ExecutionContext(storage=storage)

    while True:
        client_socket, _ = server_socket.accept()  # wait for client
        threading.Thread(
            target=handle_connection, args=(client_socket, execution_context)
        ).start()


if __name__ == "__main__":
    main()
