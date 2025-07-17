"""Abstract classes that define storage functionalities that are implemented by
a redis store."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntEnum


class RedisEncoding(IntEnum):
    """One byte flag that indicates the encoding used to save bytes."""

    STRING = 0
    LIST = 1
    SET = 2
    ZSET = 3
    HASH = 4
    ZIPMAP = 9
    ZIPLIST = 10
    INTSET = 11
    ZSET_ZIPLIST = 12
    HASH_ZIPLIST = 13
    LIST_QUICKLIST = 14


@dataclass
class RedisValue:
    expiry: int | None  # unix timestamp when the key-value pair expires
    value: bytes  # actual value in raw bytes
    encoding: RedisEncoding = RedisEncoding.STRING # default string encoding


class RedisStorage(ABC):
    @abstractmethod
    def get(self, key: bytes) -> RedisValue:
        """Get value of previously stored key, return Nil if no such key
        exists."""
        raise NotImplementedError

    @abstractmethod
    def set(
        self, key: bytes, value: RedisValue
    ):  # should value be deserializable as well?
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
