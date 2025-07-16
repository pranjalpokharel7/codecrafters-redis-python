import socket  # noqa: F401
import sys
import threading

from app.args import get_arg_parser
from app.config import Config
from app.context import ExecutionContext
from app.logger import log
from app.storage.in_memory import ThreadSafeStorage as Storage
from app.types.resp import resp_type_from_bytes
from app.utils import parsed_input_to_command

MAX_BUF_SIZE = 512


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
        # close connection on any exception that the thread can not recover from
        log.error(f"encountered an error: {e}")
        log.error("closing client connection")
        client_socket.close()
        raise e # only for debugging 


def main():
    # start tcp server
    port = 6379
    server_socket = socket.create_server(("localhost", port), reuse_port=True)
    log.info(f"started server at port: {port}")

    # parse arguments
    arg_parser = get_arg_parser()
    args = arg_parser.parse_args(sys.argv[1:])  # skip script name

    # initialize context
    storage = Storage()
    config = Config(dir=args.dir, dbfilename=args.dbfilename)
    execution_context = ExecutionContext(storage=storage, config=config)

    while True:
        client_socket, address = server_socket.accept()  # wait for client
        log.info(f"client connected: {address}")

        threading.Thread(
            target=handle_connection, args=(client_socket, execution_context)
        ).start()


if __name__ == "__main__":
    main()
