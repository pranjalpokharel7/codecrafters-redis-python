import socket  # noqa: F401
import threading

from app.exec.base import ExecutionContext
from app.storage.in_memory import ThreadSafeStorage as Storage
from app.types.resp import resp_type_from_bytes
from app.utils import parsed_input_to_command

MAX_BUF_SIZE = 512


def handle_connection(client_socket: socket.socket, ctx: ExecutionContext):
    while True:
        buf = client_socket.recv(MAX_BUF_SIZE)
        if not buf:  # empty buffer means client has disconnected
            break

        parsed_input, _ = resp_type_from_bytes(buf)
        command = parsed_input_to_command(parsed_input)
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
