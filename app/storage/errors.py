class StorageError(BaseException):
    pass


class KeyDoesNotExist(StorageError):
    def __init__(self, key: bytes) -> None:
        super().__init__(f"key={key} does not exist")


class KeyExpired(StorageError):
    def __init__(self, key: str) -> None:
        super().__init__(f"key={key} expired")
