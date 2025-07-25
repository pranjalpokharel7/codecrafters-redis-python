import logging
import threading

from app.context import ConnectionContext, ExecutionContext
from app.replica.slave import ReplicaSlave
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
        replica = ReplicaSlave(
            master_host=master_host,
            master_port=master_port,
            listening_port=listening_port,
        )

        # establish connection with master
        replica.handshake(exec_ctx)
        conn_ctx = ConnectionContext(sock=replica.sock, is_replica_connection=True)

        # listen to incoming response from master on a background thread
        threading.Thread(
            target=handle_connection,
            args=(conn_ctx, exec_ctx, replica.buf),
        ).start()

    except Exception as e:
        logging.error(f"failed to connect to master replica: {e}")
        raise e
