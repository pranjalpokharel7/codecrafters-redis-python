"""SimpleStorage is a non-thread-safe, in-memory key-value store implementation
of RedisStorage.

Intended for use in single-threaded contexts such as testing, it
provides basic set, get, and remove operations without locking
mechanisms.
"""

import fnmatch
import re
from time import time
from typing import Callable

from app.storage.in_memory.base import RedisStorage
from app.storage.in_memory.errors import (
    InvalidKeyFormat,
    InvalidValueFormat,
    KeyDoesNotExist,
    KeyExpired,
)
from app.storage.types import RedisValue


class SimpleStorage(RedisStorage):
    def __init__(self, db: dict | None = None):
        self.db = db or {}

    def _raise_if_expired(self, key: bytes, value: RedisValue):
        expiry = value.expiry
        if expiry and expiry < int(time() * 1000):
            del self.db[key]
            raise KeyExpired(key)

    def _get_value(self, key: bytes) -> RedisValue:
        value = self.db.get(key)
        if not value:
            raise KeyDoesNotExist(key)
        self._raise_if_expired(key, value)
        return value

    def _validate_db(self, db: dict[bytes, RedisValue]):
        for k, v in db.items():
            if not isinstance(k, bytes):
                raise InvalidKeyFormat
            if not isinstance(v, RedisValue):
                raise InvalidValueFormat

    def get(self, key: bytes) -> RedisValue:
        return self._get_value(key)

    def set(self, key: bytes, value: RedisValue):
        self.db[key] = value

    def remove(self, key: bytes):
        self.db.pop(key, None)

    def keys(self, pattern: bytes | None = None) -> list[bytes]:
        if pattern:
            try:
                regex = re.compile(fnmatch.translate(pattern.decode()).encode())
                return [k for k in self.db if regex.fullmatch(k)]
            except UnicodeDecodeError:
                return []
        return list(self.db)

    def update(self, key: bytes, fn: Callable[[RedisValue], RedisValue]) -> RedisValue:
        value = self._get_value(key)
        updated = fn(value)
        self.db[key] = updated
        return updated

    def restore(self, db: dict[bytes, RedisValue]):
        self._validate_db(db)
        self.db = db
