from dataclasses import dataclass
from typing import Union

from typing_extensions import Self

from app.resp.parser import cr_parser
from app.resp.base import RESPType
from app.resp.constants import (
    SB_ARRAY,
    SB_BULK_STRING,
    SB_INTEGER,
    SB_SIMPLE_ERROR,
    SB_SIMPLE_STRING,
)
from app.resp.errors import EmptyBuffer, InvalidStartingByte 
from app.resp.types.bulk_string import BulkString
from app.resp.types.integer import Integer
from app.resp.types.simple_error import SimpleError
from app.resp.types.simple_string import SimpleString


@dataclass
class Array(RESPType):
    value: list
    start_byte = SB_ARRAY

    def __bytes__(self) -> bytes:
        out = [f"*{len(self.value)}\r\n".encode()]
        out.extend(bytes(element) for element in self.value)
        return b"".join(out)

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple[Self, int]:
        """Deserializes bytes to RESP Array type.

        Args:
            data (bytes): The byte buffer to deserialize, expected format: b"*<count>\r\n<element-1>...<element-n>"

        Returns:
            tuple[Self, int]: Instance of self and the updated buffer position after parsing.

        Exceptions:
            Specific to data validation (see validate() method in base class `Deserializable`)
        """
        cls.validate(data)
        parser = cr_parser(data)
        count_bytes, pos = next(parser)
        count = int(count_bytes[1:].decode())  # skip starting byte

        array = []
        for _ in range(count):
            if pos >= len(data):
                raise EOFError("Unexpected EOF")# encountered end of buffer before parsing complete

            element, offset = bytes_to_resp(data, pos)
            array.append(element)
            pos += offset

        return cls(array), pos


# Union type
RespElement = Union[Integer, BulkString, SimpleString, SimpleError, Array]


def bytes_to_resp(data: bytes, pos: int = 0) -> tuple[RespElement, int]:
    """Utility function that parses bytes to appropriate RESP type.

    Args:
        data (bytes): The byte buffer to deserialize.
        pos (int, optional): The starting position in the byte buffer. Defaults to 0.

    Returns:
        tuple[RespElement, int]: A tuple of a `RespElement` and the updated buffer position after parsing.

    Exceptions:
        EmptyBuffer: If the provided data is empty.
        InvalidStartingByte: If the starting byte is not recognized.
    """
    if len(data) == 0:
        raise EmptyBuffer

    starting_byte = data[pos]
    if starting_byte == ord(SB_SIMPLE_STRING):
        return SimpleString.from_bytes(data[pos:])
    elif starting_byte == ord(SB_SIMPLE_ERROR):
        return SimpleError.from_bytes(data[pos:])
    elif starting_byte == ord(SB_INTEGER):
        return Integer.from_bytes(data[pos:])
    elif starting_byte == ord(SB_BULK_STRING):
        return BulkString.from_bytes(data[pos:])
    elif starting_byte == ord(SB_ARRAY):
        return Array.from_bytes(data[pos:])
    else:
        raise InvalidStartingByte(starting_byte)
