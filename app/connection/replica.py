import logging
import threading

from app.context import ConnectionContext, ExecutionContext
from app.replication.handshake import ReplicaHandshakeClient
from app.connection.common import handle_connection


def connect_to_master_replica(
    master_host: str,
    master_port: int,
    listening_port: int,
    exec_ctx: ExecutionContext,
):
    """This function connects to a master replica and spawns a background
    thread listening for messages from the master."""
    try:
        client = ReplicaHandshakeClient(
            master_host=master_host,
            master_port=master_port,
            listening_port=listening_port,
        )

        # establish connection with master and update offset and in-memory storage
        master_offset, master_rdb_snapshot = client.handshake()
        exec_ctx.info.add_to_offset(master_offset)
        exec_ctx.rdb.restore_storage_from_snapshot(
            master_rdb_snapshot, exec_ctx.storage
        )

        conn_ctx = ConnectionContext(sock=client.sock, is_connection_to_master=True)

        # listen to incoming response from master on a background thread
        threading.Thread(
            target=handle_connection,
            args=(conn_ctx, exec_ctx, client.buf),
        ).start()

    except Exception as e:
        logging.error(f"failed to connect to master replica: {e}")
        raise e
