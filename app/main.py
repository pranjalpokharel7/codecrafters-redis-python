import logging
import os
import socket
import sys
import threading

from app.args import get_arg_parser
from app.config import Config
from app.context import ExecutionContext
from app.info import Info
from app.info.sections.info_replication import InfoReplication, ReplicationRole
from app.logger import *  # import for logging configuration
from app.pool import ConnectionPool
from app.storage.in_memory import ThreadSafeStorage as Storage
from app.storage.rdb import RDBManager
from app.utils.connection import accept_client_connections, connect_to_master_replica


def main():
    # parse arguments and start server
    args = get_arg_parser().parse_args(sys.argv[1:])
    server_socket = socket.create_server(("localhost", args.port), reuse_port=True)
    logging.info(f"started server at port: {args.port}")

    # initialize config
    config = Config(dir=args.dir, dbfilename=args.dbfilename)

    # initialize storage
    storage = Storage()
    rdb = RDBManager()
    if config.dir and config.dbfilename:
        path = os.path.join(config.dir, config.dbfilename)
        rdb.restore_from_file(path, storage)

    # initialize info
    info_replication = InfoReplication()
    if replicaof := args.replicaof:
        info_replication.role = ReplicationRole.SLAVE
    info = Info(info_replication)

    # initialize execution context
    exec_context = ExecutionContext(
        storage=storage,
        config=config,
        info=info,
        rdb=rdb,
        pool=ConnectionPool(),
    )

    # start accepting client connections
    threading.Thread(
        target=accept_client_connections, args=(server_socket, exec_context)
    ).start()

    # connect to master replica
    if info.server_role() == ReplicationRole.SLAVE:
        connect_to_master_replica(
            master_host=replicaof["host"],
            master_port=replicaof["port"],
            listening_port=args.port,
            exec_ctx=exec_context,
        )


if __name__ == "__main__":
    main()
