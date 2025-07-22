import logging
import socket
import threading
from dataclasses import dataclass
from time import time


@dataclass
class Connection:
    """Class used to represent a connection in the connection pool."""

    uid: str  # unique id for the connection
    sock: socket.socket  # actual socket used for connection
    last_ack_offset: int = 0  # track the last acknowledged offset (for replica)


class ConnectionPool:
    """This class is used to manage persistent connections opened by clients.

    This will allow us to avoid re-establishing connections in intervals
    and also allow us to send messages from master to slave replicas.
    """

    # maintain a pool of connections key-ed by some unique id
    # so that pool list can be easily removed/updated
    _pool: dict[str, Connection]

    def __init__(self) -> None:
        self._pool = {}
        self._lock = threading.Lock()  # required when we need to update the info

    def add(self, uid: str, sock: socket.socket):
        with self._lock:
            logging.info(f"saving connection {uid} to pool")
            self._pool[uid] = Connection(uid, sock)

    def remove(self, uid: str):
        with self._lock:
            if uid in self._pool:
                logging.error(f"connection {uid} removed from pool")
                self._pool[uid].sock.close()
                del self._pool[uid]

    def get(self, uid: str) -> Connection | None:
        with self._lock:
            return self._pool.get(uid)

    def send_getack(self, min_offset: int):
        payload = b"*3\r\n$8\r\nREPLCONF\r\n$6\r\nGETACK\r\n$1\r\n*\r\n"
        with self._lock:
            for conn in self._pool.values():
                if conn.last_ack_offset >= min_offset:
                    continue  # Already up to date
                try:
                    conn.sock.sendall(payload)
                except Exception as e:
                    logging.warning(f"GETACK failed for {conn.uid}: {e}")

    def acked_replicas(self, min_offset: int) -> int:
        """This returns the number of replicas that have successfully
        acknowledged the most recent offset (min_offset)."""
        with self._lock:
            return sum(
                1 for conn in self._pool.values() if conn.last_ack_offset >= min_offset
            )

    def propagate(self, data: bytes):
        """Forwards data to all connections.

        Returns the number of successful replicas the message was
        forwarded to.
        """
        with self._lock:
            connections = self._pool.values()
            for conn in connections:
                try:
                    logging.info(f"sending {data} to {conn.uid}")
                    conn.sock.sendall(data)

                except Exception as e:
                    logging.error(f"connection {conn.uid} removed from pool - {e}")
                    self._pool[conn.uid].sock.close()
                    del self._pool[conn.uid]
