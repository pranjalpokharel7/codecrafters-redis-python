from dataclasses import dataclass

from app.config import Config
from app.info import Info
from app.pool import ConnectionPool
from app.storage.in_memory.base import RedisStorage
from app.storage.rdb.manager import RDBManager
from app.queue import TransactionQueue


@dataclass
class ExecutionContext:
    """
    References to objects that are shared across all connections (threads).
    """
    storage: RedisStorage
    config: Config
    info: Info
    rdb: RDBManager
    pool: ConnectionPool


@dataclass
class ConnectionContext:
    """References to objects that are specific to a connection and are
    accessible as long as the connection is alive."""
    uid: str
    tx_queue: TransactionQueue
