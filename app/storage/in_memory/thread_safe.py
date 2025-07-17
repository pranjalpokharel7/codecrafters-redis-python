"""InMemoryDB is a thread-safe wrapper around SimpleStorage.

It extends the non-thread-safe SimpleStorage by adding locking
mechanisms, making it suitable for multi-threaded contexts.
"""

import threading

from app.storage.in_memory.base import RedisValue
from app.storage.in_memory.simple import SimpleStorage


class ThreadSafeStorage(SimpleStorage):
    def __init__(self, db: dict | None = None):
        self.lock = threading.Lock()
        with self.lock:
            super().__init__(db)

    def set(self, key: bytes, value: RedisValue):
        with self.lock:
            super().set(key, value)

    def get(self, key: bytes) -> RedisValue:
        with self.lock:
            return super().get(key)

    def remove(self, key: bytes):
        with self.lock:
            super().remove(key)

    def keys(self, pattern: bytes | None = None) -> list[bytes]:
        with self.lock:
            return super().keys(pattern)
