from dataclasses import dataclass

from app.storage.base import RedisStorage
from app.config import Config


@dataclass
class ExecutionContext:
    storage: RedisStorage
    config: Config
