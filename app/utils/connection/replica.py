import logging
import threading

from app.context import ExecutionContext
from app.replication.slave import ReplicaSlave
from app.utils.connection.common import handle_connection


def connect_to_master_replica(
    master_host: str,
    master_port: int,
    listening_port: int,
    execution_context: ExecutionContext,
):
    """This function connects to a master replica and spawns a background
    thread listening for messages from the master."""
    try:
        replica = ReplicaSlave(
            master_host=master_host,
            master_port=master_port,
            listening_port=listening_port,
        )

        replica.handshake()

        # all propagated commands from master will be listened to by this thread
        threading.Thread(
            target=handle_connection, args=(replica.sock, execution_context, False)
        ).start()

    except Exception as e:
        logging.error(f"failed to connect to master replica: {e}")
