"""Abstract classes that define storage functionalities that are implemented by
a redis store."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

@dataclass
class RedisValue:
    expiry: int | None # unix timestamp when the key-value pair expires
    value: bytes # actual value in raw bytes


class RedisStorage(ABC):
    @abstractmethod
    def get(self, key: bytes) -> RedisValue:
        """Get value of previously stored key, return Nil if no such key
        exists."""
        raise NotImplementedError

    @abstractmethod
    def set(self, key: bytes, value: Any):  # should value be deserializable as well?
        """Set value for a key, rewrites existing contents if key exists
        already."""
        raise NotImplementedError

    @abstractmethod
    def remove(self, key: bytes):
        """Removes key from database."""
        raise NotImplementedError
