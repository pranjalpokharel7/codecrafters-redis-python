class RDBError(Exception):
    """Base exception for all RDB parsing and serialization errors."""

    pass


class InvalidMagicByte(RDBError):
    def __init__(self, magic: bytes) -> None:
        super().__init__(f"invalid magic byte: expected b'REDIS', got {magic}")


class InvalidVersionNumber(RDBError):
    def __init__(self, version: bytes) -> None:
        super().__init__(
            f"invalid version number: expected byte encoded integer, got {version}"
        )


class UnexpectedEOF(RDBError):
    def __init__(self, index: int) -> None:
        super().__init__(f"encountered unexpected EOF at pos - {index}")


class UnknownEncoding(RDBError):
    def __init__(self, err: str = "") -> None:
        super().__init__(f"unknown encoding - {err}")
