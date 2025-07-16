"""InMemoryDB is a thread-safe wrapper around SimpleStorage.

It extends the non-thread-safe SimpleStorage by adding locking
mechanisms, making it suitable for multi-threaded contexts.
"""

import threading
from typing import Any

from app.storage.in_memory.simple import SimpleStorage


class ThreadSafeStorage(SimpleStorage):
    def __init__(self):
        super().__init__()
        self.lock = threading.Lock()

    def set(self, key: bytes, value: Any):
        with self.lock:
            super().set(key, value)

    def get(self, key: bytes):
        with self.lock:
            return super().get(key)

    def remove(self, key: bytes):
        with self.lock:
            super().remove(key)
