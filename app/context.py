from dataclasses import dataclass

from app.config import Config
from app.info import Info
from app.pool import ConnectionPool
from app.storage.in_memory.base import RedisStorage
from app.storage.rdb.manager import RDBManager


@dataclass
class ExecutionContext:
    storage: RedisStorage
    config: Config
    info: Info
    rdb: RDBManager
    pool: ConnectionPool
