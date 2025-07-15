from dataclasses import dataclass
from typing_extensions import Self

from app.parser.cr_parser import cr_parser
from app.types.base import Deserializable, Serializable, RESPType
from app.types.constants import SB_BULK_STRING


@dataclass
class BulkString(RESPType, Serializable, Deserializable):
    value: bytes = b""  # bulk string can be non-utf8 data, store as binary
    start_byte = SB_BULK_STRING

    def __bytes__(self) -> bytes:
        # null bulk string
        if not self.value:
            return b"$-1\r\n"

        length = len(self.value)
        return f"${length}\r\n".encode() + self.value + b"\r\n"

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple[Self, int]:
        """
        Deserializes bytes to RESP Bulk String type.

        Args:
            data (bytes): The byte buffer to deserialize, expected format: b"$<length>\r\n<data>\r\n"

        Returns:
            tuple[Self, int]: Instance of self and the updated buffer position after parsing.

        Exceptions:
            Specific to data validation (see validate() method in base class `Deserializable`)
        """
        cls.validate(data)
        parser = cr_parser(data)
        length_bytes, pos = next(parser)
        length = int(length_bytes[1:].decode())  # skip starting byte
        end = pos + length
        return cls(data[pos:end]), end + 2

    def __str__(self) -> str:
        """
        Decode internal bulk string value to utf-8 string (can raise an exception for binary data).
        Catch `UnicodeDecodeError` on call site.
        """
        return self.value.decode()
