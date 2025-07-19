import os
import socket
from io import BytesIO

from app.commands import NAME_TO_COMMANDS_MAP
from app.commands.base import RedisCommand
from app.commands.errors import CommandEmpty, UnrecognizedCommand
from app.context import ExecutionContext
from app.logger import log
from app.resp.types import Array, RespElement
from app.resp.types.array import resp_type_from_bytes
from app.resp.types.simple_error import SimpleError
from app.storage.rdb.parser import RDBParser

MAX_BUF_SIZE = 512  # this should be a config parameter


def parsed_input_to_command(parsed_input: RespElement) -> RedisCommand:
    """Creates a RedisCommand from the given RESP Element.

    Throws an exception if the element is not a RESP Array (for now,
    will be handled later if needed).
    """
    if not isinstance(parsed_input, Array):
        # unsure if there are future instances that will receive commands in non-array form
        raise ValueError("invalid command format: expected serialized RESP array")

    array = parsed_input.value
    if len(array) < 1:
        raise CommandEmpty

    # perform longer prefix match first if there are cases of common prefix
    # for eg, CMD and CMD RUN (both fictional commands, just for example)

    # shorter prefix match for single command names
    command_name = array[0].value
    if command_name in NAME_TO_COMMANDS_MAP:
        log.info(f"received command: {command_name}")
        mapped_command = NAME_TO_COMMANDS_MAP[command_name]
        return mapped_command([element.value for element in array[1:]])

    # longer prefix match for compound commands
    subcommand_name = array[1].value if len(array) > 1 else b""
    compound_command_key = command_name + b" " + subcommand_name
    if compound_command_key in NAME_TO_COMMANDS_MAP:
        log.info(f"received command: {compound_command_key}")
        mapped_command = NAME_TO_COMMANDS_MAP[compound_command_key]
        return mapped_command([element.value for element in array[2:]])

    # command not recognized (or not implemented yet) internally
    raise UnrecognizedCommand(command_name)


def load_from_rdb_file(path: str, read_threshold: int = 10 * 10 * 1024) -> dict:
    """Loads RDB file and returns as dict for storage initialization.

    path: path to file
    read_threshold: (optional) argument that sets the threshold for
                    reading entire file into memory (if file size is lesser than threshold)
                    or return a buffered reader to disk
    """
    try:
        file_size = os.path.getsize(path)
        with open(path, "rb") as f:
            if file_size <= read_threshold:
                buf = f.read()
                reader = BytesIO(buf)
            else:
                reader = f

            return RDBParser(reader).db

    except FileNotFoundError:
        # ignore if backup file doesn't exist
        return {}


def handle_connection(client_socket: socket.socket, ctx: ExecutionContext):
    try:
        while True:
            buf = client_socket.recv(MAX_BUF_SIZE)
            if not buf:  # empty buffer means client has disconnected
                break

            parsed_input, _ = resp_type_from_bytes(buf)
            command = parsed_input_to_command(parsed_input)
            response = command.exec(ctx)

            # commands like psync return multiple responses
            if isinstance(response, list):
                for res in response:
                    log.info(f"sending response: {res}")
                    client_socket.sendall(res)
            else:
                log.info(f"sending response: {response}")
                client_socket.sendall(response)

    except Exception as e:
        # send error to client and close connection
        client_socket.sendall(bytes(SimpleError(str(e).encode())))
        client_socket.close()
        log.exception(e)
