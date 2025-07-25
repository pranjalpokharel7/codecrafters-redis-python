import logging
import socket
import threading
from dataclasses import dataclass
from time import time


@dataclass
class ReplicaConnection:
    """Class used to represent a replica connection."""

    uid: str  # unique id for the connection
    sock: socket.socket  # actual socket used for connection
    last_ack_offset: int = 0  # track the last acknowledged offset (for replica)
    awaiting_ack_offset: int | None = None  # time since waiting for an ack of offset


class ReplicaConnectionPool:
    """Manages persistent connections for sending requests from master to replicas (server-to-client)."""

    # maintain a pool of connections key-ed by some unique id
    # so that pool list can be easily removed/updated
    _pool: dict[str, ReplicaConnection]

    def __init__(self) -> None:
        self._pool = {}
        self._lock = threading.RLock()  # use re-entrant lock

    def add(self, uid: str, sock: socket.socket):
        with self._lock:
            logging.info(f"adding replica connection {uid} to pool")
            self._pool[uid] = ReplicaConnection(uid, sock)

    def remove(self, uid: str):
        with self._lock:
            conn = self._pool.pop(uid, None)
            if conn:
                logging.warning(f"replica connection {uid} removed from pool")
                conn.sock.close()

    def request_offset_ack_from_connections(self, min_offset: int):
        """
        Request acknowledgement of latest offset from each replica.
        """
        GET_ACK = b"*3\r\n$8\r\nREPLCONF\r\n$6\r\nGETACK\r\n$1\r\n*\r\n"
        ACK_WAIT_FOR_MS = 200

        with self._lock:
            for conn in self._pool.values():
                if conn.last_ack_offset >= min_offset:
                    continue

                # if connection has been waiting for offset acknowledgement for
                # less than waiting time, skip sending another ack request for now
                if (
                    conn.awaiting_ack_offset
                    and int(time() * 1000) - conn.awaiting_ack_offset < ACK_WAIT_FOR_MS
                ):
                    continue

                try:
                    conn.sock.sendall(GET_ACK)
                    conn.awaiting_ack_offset = int(time() * 1000)
                except Exception as e:
                    logging.warning(f"GETACK failed for {conn.uid}: {e}")

    def update_last_ack_offset(self, uid: str, offset: int):
        """Updates the last acknowledged offset received from a replica."""
        with self._lock:
            if uid in self._pool:
                self._pool[uid].last_ack_offset = offset
                self._pool[uid].awaiting_ack_offset = None

    def count_acked_connections(self, min_offset: int) -> int:
        """This returns the number of replicas that have successfully
        acknowledged the most recent offset (min_offset)."""
        with self._lock:
            return sum(
                1 for conn in self._pool.values() if conn.last_ack_offset >= min_offset
            )

    def broadcast_to_all_connections(self, data: bytes) -> int:
        """Forwards data to all connections.

        Returns the number of successful replicas the message was
        forwarded to.
        """
        with self._lock:
            success = 0
            for uid, conn in list(self._pool.items()):
                try:
                    conn.sock.sendall(data)
                    success += 1
                except Exception as e:
                    logging.error(f"Failed to send to {uid}: {e}")
                    self._pool[conn.uid].sock.close()
                    del self._pool[conn.uid]

            return success
