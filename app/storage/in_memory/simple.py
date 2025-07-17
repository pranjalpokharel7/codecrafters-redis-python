"""SimpleStorage is a non-thread-safe, in-memory key-value store implementation
of RedisStorage.

Intended for use in single-threaded contexts such as testing, it
provides basic set, get, and remove operations without locking
mechanisms.
"""

import re
import fnmatch

from app.storage.base import RedisStorage, RedisValue
from app.storage.errors import KeyDoesNotExist


class SimpleStorage(RedisStorage):
    db: dict[bytes, RedisValue]

    def __init__(self, db: dict | None = None):
        self.db = db or {}  # optionally initialize with values

    def set(self, key: bytes, value: RedisValue):
        self.db[key] = value

    def get(self, key: bytes) -> RedisValue:
        value = self.db.get(key)
        if not value:
            raise KeyDoesNotExist(key)
        return value

    def remove(self, key: bytes):
        if key in self.db:
            del self.db[key]

    def keys(self, pattern: bytes | None = None) -> list[bytes]:
        if pattern:
            # we can't use fnmatch directly because keys are binary-safe
            # i.e. they aren't always utf-8 encoded bytes (decoding can fail)
            # decode if it affects performance and use fnmatch (?)
            pattern = fnmatch.translate(pattern.decode()).encode()  # sanitize pattern
            match_pattern = re.compile(pattern)  # compile for efficiency in reuse
            return [k for k in self.db.keys() if match_pattern.fullmatch(k)]

        # return entire list of keys
        return list(self.db.keys())
