"""
InMemoryDB is a thread-safe, in-memory key-value store.
"""

import threading
from typing import Any
from app.storage.base import RedisStorage
from app.storage.errors import KeyDoesNotExist

class InMemoryDB(RedisStorage):
    def __init__(self):
        self.db = {}
        self.lock = threading.Lock()

    def set(self, key: bytes, value: Any):
        with self.lock:
            self.db[key] = value

    def get(self, key: bytes):
        with self.lock:
            value = self.db.get(key)
            if not value:
                raise KeyDoesNotExist(key)
            return value

    # utility method used for removing key after expiry
    def remove(self, key: bytes):
        with self.lock:
            if key in self.db:
                del self.db[key]
