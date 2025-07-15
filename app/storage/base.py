"""
Abstract classes that define storage functionalities that are implemented by a redis store.
"""
from abc import ABC, abstractmethod
from typing import Any

class RedisStorage(ABC):
    @abstractmethod
    def get(self, key: bytes):
        raise NotImplementedError

    @abstractmethod
    def set(self, key: bytes, value: Any): # should value be deserializable as well?
        raise NotImplementedError
