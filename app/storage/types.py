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
    expiry: int | None  # unix timestamp when the key-value pair expires
    value: bytes  # actual value in raw bytes
    encoding: RedisEncoding = RedisEncoding.STRING  # default string encoding


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
