import socket
from dataclasses import dataclass, field

from app.config import Config
from app.info import Info
from app.replication.pool import ReplicaConnectionPool
from app.queue import TransactionQueue
from app.storage.in_memory.base import RedisStorage
from app.storage.rdb.manager import RDBManager


@dataclass
class ExecutionContext:
    """References to objects that are shared across all connections
    (threads)."""

    storage: RedisStorage
    config: Config
    info: Info
    rdb: RDBManager
    replica_pool: ReplicaConnectionPool


@dataclass
class ConnectionContext:
    """Context for an incoming client or replica request (client-to-server).
    References to a connection context is specific to a single thread and thus
    doesn't require access through thread locks."""

    sock: socket.socket
    is_connection_to_master: bool = False  # denotes if this is a connection to master (from a replica's perspective)
    tx_queue: TransactionQueue = field(default_factory=TransactionQueue)
    uid: str = field(init=False)

    def __post_init__(self):
        peer = self.sock.getpeername()
        if isinstance(peer, tuple) and len(peer) >= 2:  # ipv4/v6
            host, port = peer[0], peer[1]
            self.uid = f"{host}:{port}"
        else:  # unix socket
            self.uid = str(peer)
