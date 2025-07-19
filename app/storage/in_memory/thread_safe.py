"""InMemoryDB is a thread-safe wrapper around SimpleStorage.

It extends the non-thread-safe SimpleStorage by adding locking
mechanisms, making it suitable for multi-threaded contexts.
"""

import threading

from app.storage.in_memory.base import RedisValue
from app.storage.in_memory.simple import SimpleStorage


class ThreadSafeStorage(SimpleStorage):
    def __init__(self, db: dict | None = None):
        self._lock = threading.Lock()
        with self._lock:
            super().__init__(db)

    def set(self, key: bytes, value: RedisValue):
        with self._lock:
            super().set(key, value)

    def get(self, key: bytes) -> RedisValue:
        with self._lock:
            return super().get(key)

    def remove(self, key: bytes):
        with self._lock:
            super().remove(key)

    def keys(self, pattern: bytes | None = None) -> list[bytes]:
        with self._lock:
            return super().keys(pattern)
