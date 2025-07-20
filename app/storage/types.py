from enum import IntEnum
from dataclasses import dataclass
from io import BufferedReader, BytesIO

# REFACTOR: should this be moved to specific files in in-memory and rdb folders?


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
    expiry: int | None  # unix timestamp when the key-value pair expires
    raw_bytes: bytes  # actual value in raw bytes (rename this to raw_bytes?)
    encoding: RedisEncoding = RedisEncoding.STRING  # default string encoding

    def __bytes__(self):
        return self.raw_bytes


class LengthEncodingType(IntEnum):
    """Flag that indicates the type of length encoding:

    1. Length prefixed strings
    2. An 8, 16 or 32 bit integer
    3. A LZF compressed string

    Based on the encoding type, the length encoded bytes can be further decoded.
    """

    STRING = 0
    INTEGER = 1
    COMPRESSED = 2


RDBReader = BufferedReader | BytesIO
