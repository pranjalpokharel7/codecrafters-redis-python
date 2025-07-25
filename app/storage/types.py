from enum import IntEnum
from dataclasses import dataclass
from io import BufferedReader, BytesIO


class RedisEncoding(IntEnum):
    """One byte flag that indicates the encoding used to save bytes."""

    STRING = 0
    LIST = 1
    SET = 2
    ZSET = 3
    HASH = 4
    ZIPMAP = 9
    ZIPLIST = 10
    INTSET = 11
    ZSET_ZIPLIST = 12
    HASH_ZIPLIST = 13
    LIST_QUICKLIST = 14


@dataclass
class RedisValue:
    raw_bytes: bytes  # actual value in raw bytes (rename this to raw_bytes?)
    expiry: int | None = None  # unix timestamp when the key-value pair expires
    encoding: RedisEncoding = RedisEncoding.STRING  # default string encoding

    def __bytes__(self):
        return self.raw_bytes


RDBReader = BufferedReader | BytesIO
