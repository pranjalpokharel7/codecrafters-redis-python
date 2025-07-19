import socket
import threading
import logging
from dataclasses import dataclass


@dataclass
class Connection:
    uid: str  # unique id for the connection
    sock: socket.socket  # actual socket used for connection


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
            self._pool[uid] = Connection(uid, sock)
            print(self._pool)

    def remove(self, uid: str):
        with self._lock:
            if uid in self._pool:
                # close() won't raise an error even if socket is already closed
                self._pool[uid].sock.close()
                del self._pool[uid]

    def get(self, uid: str) -> Connection | None:
        with self._lock:
            return self._pool.get(uid)

    def propagate(self, data: bytes):
        """Forwards data to all connections."""
        with self._lock:
            connections = self._pool.values()
            for conn in connections:
                try:
                    conn.sock.sendall(data)
                except Exception as e:
                    # if encountered exception while sending data, 
                    # close connection and remove from connections pool
                    logging.error(f"connection {conn.uid} removed from pool - {e}")
                    self._pool[conn.uid].sock.close()
                    del self._pool[conn.uid]
                    
