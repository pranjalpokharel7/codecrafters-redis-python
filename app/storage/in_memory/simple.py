"""SimpleStorage is a non-thread-safe, in-memory key-value store implementation
of RedisStorage.

Intended for use in single-threaded contexts such as testing, it
provides basic set, get, and remove operations without locking
mechanisms.
"""

from typing import Any

from app.storage.base import RedisStorage
from app.storage.errors import KeyDoesNotExist


class SimpleStorage(RedisStorage):
    def __init__(self):
        self.db = {}

    def set(self, key: bytes, value: Any):
        self.db[key] = value

    def get(self, key: bytes):
        value = self.db.get(key)
        if not value:
            raise KeyDoesNotExist(key)
        return value

    def remove(self, key: bytes):
        if key in self.db:
            del self.db[key]
