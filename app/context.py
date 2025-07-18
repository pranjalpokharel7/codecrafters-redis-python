from dataclasses import dataclass

from app.storage.in_memory.base import RedisStorage
from app.config import Config
from app.info import Info


@dataclass
class ExecutionContext:
    storage: RedisStorage
    config: Config
    info: Info
