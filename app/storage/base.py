"""Abstract classes that define storage functionalities that are implemented by
a redis store."""

from abc import ABC, abstractmethod
from typing import Any


class RedisStorage(ABC):
    @abstractmethod
    def get(self, key: bytes):
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
