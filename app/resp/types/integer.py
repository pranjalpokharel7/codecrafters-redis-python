from dataclasses import dataclass
from typing_extensions import Self

from app.resp.parser import cr_parser
from app.resp.base import RESPType, Deserializable, Serializable
from app.resp.constants import SB_INTEGER


@dataclass
class Integer(RESPType, Serializable, Deserializable):
    value: bytes
    start_byte = SB_INTEGER

    def __bytes__(self) -> bytes:
        return f":{int(self.value)}\r\n".encode()

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple[Self, int]:
        """
        Deserializes bytes to RESP Integer type.

        Args:
            data (bytes): The byte buffer to deserialize, expected format: b":[<+|->]<value>\r\n"

        Returns:
            tuple[Self, int]: Instance of self and the updated buffer position after parsing.

        Exceptions:
            Specific to data validation (see validate() method in base class `Deserializable`)
        """
        cls.validate(data)
        parser = cr_parser(data)
        value, pos = next(parser)
        return cls(value[1:]), pos  # skip starting byte

    def __int__(self):
        int(self.value)
