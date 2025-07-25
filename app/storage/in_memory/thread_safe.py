"""InMemoryDB is a thread-safe wrapper around SimpleStorage. This class does
not modify behavior or extend functionality of SimpleStorage, but ensures
thread-safe access using a global lock.

It extends the non-thread-safe SimpleStorage by adding locking
mechanisms, making it suitable for multi-threaded contexts.
"""

import threading
from typing import Callable

from app.storage.in_memory.simple import SimpleStorage
from app.storage.types import RedisValue


class ThreadSafeStorage(SimpleStorage):
    def __init__(self, db: dict | None = None):
        self._lock = threading.RLock()  # use a re-entrant lock
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

    def update(self, key: bytes, fn: Callable[[RedisValue], RedisValue]) -> RedisValue:
        with self._lock:
            return super().update(key, fn)

    def restore(self, db: dict[bytes, RedisValue]):
        with self._lock:
            return super().restore(db)
