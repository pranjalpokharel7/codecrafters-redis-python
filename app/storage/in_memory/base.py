"""Abstract classes that define storage functionalities that are implemented by
a redis store."""

from abc import ABC, abstractmethod
from typing import Callable

from app.storage.types import RedisValue


class RedisStorage(ABC):
    @abstractmethod
    def get(self, key: bytes) -> RedisValue:
        """Get value of previously stored key, return Nil if no such key
        exists."""
        raise NotImplementedError

    @abstractmethod
    def set(self, key: bytes, value: RedisValue):
        """Set value for a key, rewrites existing contents if key exists
        already."""
        raise NotImplementedError

    @abstractmethod
    def remove(self, key: bytes):
        """Removes key from database."""
        raise NotImplementedError

    @abstractmethod
    def keys(self, pattern: bytes | None = None) -> list[bytes]:
        """Returns all keys in the database that match the pattern."""
        raise NotImplementedError

    @abstractmethod
    def update(self, key: bytes, fn: Callable[[RedisValue], RedisValue]) -> RedisValue:
        """Provide an update function that is applied to the key stored in the
        database."""
        raise NotImplementedError

    @abstractmethod
    def restore(self, db: dict[bytes, RedisValue]):
        """Restore db contents."""
        raise NotImplementedError
