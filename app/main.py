import socket  # noqa: F401
import threading

from app.exec import NAME_TO_COMMANDS_MAP
from app.exec.base import ExecutionContext, RedisCommand
from app.exec.errors import CommandEmpty, UnrecognizedCommand
from app.storage.in_memory import ThreadSafeStorage as Storage
from app.types.resp import Array, RespElement, resp_type_from_bytes

MAX_BUF_SIZE = 512


def parsed_input_to_command(parsed_input: RespElement) -> RedisCommand:
    """Creates a RedisCommand from the given RESP Element.

    Throws an exception if the element is not a RESP Array (for now,
    will be handled later if needed).
    """
    if not isinstance(parsed_input, Array):
        # unsure if there are future instances that will receive commands in non-array form
        raise Exception("invalid command format: expected serialized RESP array")

    array = parsed_input.value
    if len(array) < 1:
        raise CommandEmpty

    command_name = array[0].value
    subcommand_name = array[1].value if len(array) > 1 else b""

    # Reorder the checks for prefix matching if we don't have
    # compound and simple command names starting from the same prefix
    # (eg: ACL and ACL CAT - are these two different commands?)

    # Longest prefix match for compound commands
    compound_command_key = command_name + b" " + subcommand_name
    if compound_command_key in NAME_TO_COMMANDS_MAP:
        mapped_command = NAME_TO_COMMANDS_MAP[compound_command_key]
        return mapped_command([element.value for element in array[2:]])

    # Shorter prefix match for single command names
    elif command_name in NAME_TO_COMMANDS_MAP:
        mapped_command = NAME_TO_COMMANDS_MAP[command_name]
        return mapped_command([element.value for element in array[1:]])

    else:
        raise UnrecognizedCommand(command_name)


def handle_connection(client_socket: socket.socket, ctx: ExecutionContext):
    while True:
        chunk = client_socket.recv(MAX_BUF_SIZE)
        if not chunk:  # empty buffer means client has disconnected
            break

        parsed_input, _ = resp_type_from_bytes(chunk)
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
