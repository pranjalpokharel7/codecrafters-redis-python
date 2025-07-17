from dataclasses import dataclass

from typing_extensions import Self

from app.resp.parser import cr_parser
from app.resp.base import Deserializable, RESPType, Serializable
from app.resp.constants import SB_SIMPLE_STRING


@dataclass
class SimpleString(RESPType, Serializable, Deserializable):
    value: bytes  # store as binary string to avoid unnecessary encoding/decoding
    start_byte = SB_SIMPLE_STRING

    def __bytes__(self) -> bytes:
        return b"+" + self.value + b"\r\n"

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple[Self, int]:
        """Deserializes bytes to RESP Simple String type.

        Args:
            data (bytes): The byte buffer to deserialize, expected format: b"+<data>\r\n"

        Returns:
            tuple[Self, int]: Instance of self and the updated buffer position after parsing.

        Exceptions:
            Specific to data validation (see validate() method in base class `Deserializable`)
        """
        cls.validate(data)
        parser = cr_parser(data)
        value, pos = next(parser)
        return cls(value[1:]), pos  # skip starting byte

    def __str__(self) -> str:
        return self.value.decode()
