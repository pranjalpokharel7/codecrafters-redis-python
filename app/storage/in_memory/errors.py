"""This module defines all errors that are raised during redis storage
operations."""


class StorageException(Exception):
    pass


class KeyDoesNotExist(StorageException):
    def __init__(self, key: bytes) -> None:
        super().__init__(f"key={key} does not exist")


class KeyExpired(StorageException):
    def __init__(self, key: bytes) -> None:
        super().__init__(f"key={key} expired")


class InvalidKeyFormat(StorageException):
    def __init__(self) -> None:
        super().__init__(f"invalid key format, expected bytes")


class InvalidValueFormat(StorageException):
    def __init__(self) -> None:
        super().__init__(f"invalid value format, expected RedisValue")
