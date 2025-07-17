import os
import socket  # noqa: F401
import sys
import threading

from app.args import get_arg_parser
from app.config import Config
from app.context import ExecutionContext
from app.logger import log
from app.storage.in_memory import ThreadSafeStorage as Storage
from app.resp.types import resp_type_from_bytes
from app.resp.types.simple_error import SimpleError
from app.utils import load_from_rdb_file, parsed_input_to_command

MAX_BUF_SIZE = 512  # this should be a config parameter


def handle_connection(client_socket: socket.socket, ctx: ExecutionContext):
    try:
        while True:
            buf = client_socket.recv(MAX_BUF_SIZE)
            if not buf:  # empty buffer means client has disconnected
                break

            parsed_input, _ = resp_type_from_bytes(buf)
            command = parsed_input_to_command(parsed_input)
            response = command.exec(ctx)

            log.info(f"sending response: {response}")
            client_socket.sendall(response)

    except BaseException as e:
        # send error to client and close connection
        client_socket.sendall(bytes(SimpleError(str(e).encode())))
        client_socket.close()
        log.exception(e)


def main():
    # parse arguments
    arg_parser = get_arg_parser()
    args = arg_parser.parse_args(sys.argv[1:])  # skip script name

    # start tcp server
    server_socket = socket.create_server(("localhost", args.port), reuse_port=True)
    log.info(f"started server at port: {args.port}")

    # initialize config
    # TODO: implement a from_args() method
    config = Config(dir=args.dir, dbfilename=args.dbfilename)

    # initialize storage
    if config.dir and config.dbfilename:
        path = os.path.join(config.dir, config.dbfilename)
        storage = Storage(load_from_rdb_file(path))
    else:
        storage = Storage()

    execution_context = ExecutionContext(storage=storage, config=config)

    while True:
        client_socket, address = server_socket.accept()  # wait for client
        log.info(f"client connected: {address}")

        threading.Thread(
            target=handle_connection, args=(client_socket, execution_context)
        ).start()


if __name__ == "__main__":
    main()
