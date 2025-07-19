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

from app.storage.in_memory.base import RedisStorage, RedisValue
from app.storage.in_memory.errors import InvalidKeyFormat, InvalidValueFormat, KeyDoesNotExist, KeyExpired


class SimpleStorage(RedisStorage):
    db: dict[bytes, RedisValue]

    def __init__(self, db: dict | None = None):
        self.db = db or {}  # optionally initialize with values

    def _raise_exception_for_expiry(self, key: bytes, value: RedisValue):
        """Checks if a key value pair is expired and raises an exception if
        condition holds true."""
        expiry = value.expiry
        if expiry and expiry < int(time() * 1000):  # timestamp is stored in ms
            del self.db[key]
            raise KeyExpired(key)

    def set(self, key: bytes, value: RedisValue):
        self.db[key] = value

    def get(self, key: bytes) -> RedisValue:
        value = self.db.get(key)
        if not value:
            raise KeyDoesNotExist(key)
        self._raise_exception_for_expiry(key, value)
        return value

    def remove(self, key: bytes):
        if key in self.db:
            del self.db[key]

    def keys(self, pattern: bytes | None = None) -> list[bytes]:
        if pattern:
            # we can't use fnmatch directly because keys are binary-safe
            # i.e. they aren't lways utf-8 encoded bytes (decoding can fail)
            # decode if it affects performance and use fnmatch (?)
            pattern = fnmatch.translate(pattern.decode()).encode()  # sanitize pattern
            match_pattern = re.compile(pattern)  # compile for efficiency in reuse
            return [k for k in self.db.keys() if match_pattern.fullmatch(k)]

        # return entire list of keys
        return list(self.db.keys())

    def update(self, key: bytes, fn: Callable[[RedisValue], RedisValue]) -> RedisValue:
        """Applies an update function to a key's value.

        Any error/exception raised as a result of calling the function
        must be handled at the calling site.
        """
        value = self.db.get(key)
        if not value:
            raise KeyDoesNotExist(key)
        self._raise_exception_for_expiry(key, value)
        
        # update the value and return it
        updated = fn(value)
        self.db[key] = updated
        return updated

    def restore(self, db: dict[bytes, RedisValue]):
        # validate key-value pairs
        for k, v in db.items():
            if not isinstance(k, bytes):
                raise InvalidKeyFormat
            if not isinstance(v, RedisValue):
                raise InvalidValueFormat

        self.db = db
