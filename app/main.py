import os
import socket  # noqa: F401
import sys
import threading

from app.args import get_arg_parser
from app.config import Config
from app.context import ExecutionContext
from app.info import Info
from app.info.sections.info_replication import InfoReplication, ReplicationRole
from app.logger import log
from app.replication.slave import ReplicaSlave
from app.storage.in_memory import ThreadSafeStorage as Storage
from app.storage.rdb import RDBManager
from app.utils import handle_connection, load_from_rdb_file


def accept_client_connections(
    server_socket: socket.socket, execution_context: ExecutionContext
):
    while True:
        client_socket, address = server_socket.accept()
        log.info(f"client connected: {address}")
        threading.Thread(
            target=handle_connection, args=(client_socket, execution_context)
        ).start()


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

    # initialize info sections - extract them into a different function
    info_replication = InfoReplication()

    # determines if server is running in slave/master replica mode
    if replica := args.replicaof:
        info_replication.role = ReplicationRole.SLAVE

    info = Info(info_replication)
    rdb = RDBManager()
    execution_context = ExecutionContext(
        storage=storage, config=config, info=info, rdb=rdb
    )

    threading.Thread(
        target=accept_client_connections, args=(server_socket, execution_context)
    ).start()

    # --- start handshake with master replica
    # ideally we would want to set this up before client connections are established
    # but the tester tries to invoke commands as soon as the handshake is completed
    # which leads to race conditions
    if info_replication.role == ReplicationRole.SLAVE:
        try:
            replica = ReplicaSlave(
                host=replica["host"], port=replica["port"], listening_port=args.port
            )
            replica.handshake()
        except Exception as e:
            log.error(f"failed to connect to master replica: {e}")


if __name__ == "__main__":
    main()
