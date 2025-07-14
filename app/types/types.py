"""
This module provides classes representing Redis Serialization Protocol (RESP)
types SimpleString, BulkString, Integer, SimpleError, and Array. Each class contains it's
own logic for serialization/deserialization.
"""

from dataclasses import dataclass
from typing import Union
from typing_extensions import Self

from app.err import EmptyBuffer, InvalidStartingByte, UnexpectedEOF
from app.parser import cr_parse
from app.types.base import Serializable, Deserializable
from app.types.constants import (
    SB_ARRAY,
    SB_BULK_STRING,
    SB_INTEGER,
    SB_SIMPLE_ERROR,
    SB_SIMPLE_STRING,
)


@dataclass
class Integer(Serializable, Deserializable):
    value: int
    start_byte = SB_INTEGER

    def __bytes__(self) -> bytes:
        return f":{self.value}\r\n".encode()

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
        parser = cr_parse(data)
        value, pos = next(parser)
        return cls(int(value[1:])), pos  # skip starting byte


@dataclass
class SimpleString(Serializable, Deserializable):
    value: str
    start_byte = SB_SIMPLE_STRING

    def __bytes__(self) -> bytes:
        return f"+{self.value}\r\n".encode()

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple[Self, int]:
        """
        Deserializes bytes to RESP Simple String type.

        Args:
            data (bytes): The byte buffer to deserialize, expected format: b"+<data>\r\n"

        Returns:
            tuple[Self, int]: Instance of self and the updated buffer position after parsing.

        Exceptions:
            Specific to data validation (see validate() method in base class `Deserializable`)
        """
        cls.validate(data)
        parser = cr_parse(data)
        value, pos = next(parser)
        return cls(value[1:].decode()), pos # skip starting byte


@dataclass
class SimpleError(Serializable, Deserializable):
    value: str
    start_byte = SB_SIMPLE_ERROR

    def __bytes__(self) -> bytes:
        return f"-{self.value}\r\n".encode()

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple[Self, int]:
        """
        Deserializes bytes to RESP Simple Error type.

        Args:
            data (bytes): The byte buffer to deserialize, expected format: b"-<data>\r\n"

        Returns:
            tuple[Self, int]: Instance of self and the updated buffer position after parsing.

        Exceptions:
            Specific to data validation (see validate() method in base class `Deserializable`)
        """
        cls.validate(data)
        parser = cr_parse(data)
        value, pos = next(parser)
        return cls(value[1:].decode()), pos # skip starting byte


@dataclass
class BulkString(Serializable, Deserializable):
    value: str
    start_byte = SB_BULK_STRING

    def __bytes__(self) -> bytes:
        return f"${len(self.value)}\r\n{self.value}\r\n".encode()

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
        parser = cr_parse(data)
        length_bytes, pos = next(parser)
        length = int(length_bytes[1:].decode())  # skip starting byte
        end = pos + length
        return cls(data[pos:end].decode()), end + 2


@dataclass
class Array(Serializable, Deserializable):
    value: list
    start_byte = SB_ARRAY

    def __bytes__(self) -> bytes:
        out = [f"*{len(self.value)}\r\n".encode()]
        out.extend(bytes(i) for i in self.value)
        return b"".join(out)

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple[Self, int]:
        """
        Deserializes bytes to RESP Array type.

        Args:
            data (bytes): The byte buffer to deserialize, expected format: b"*<count>\r\n<element-1>...<element-n>"

        Returns:
            tuple[Self, int]: Instance of self and the updated buffer position after parsing.

        Exceptions:
            Specific to data validation (see validate() method in base class `Deserializable`)
        """
        cls.validate(data)
        parser = cr_parse(data)
        count_bytes, pos = next(parser)
        count = int(count_bytes[1:].decode())  # skip starting byte

        array = []
        for _ in range(count):
            if pos >= len(data):
                raise UnexpectedEOF  # encountered end of buffer before parsing complete

            element, offset = resp_type_from_bytes(data, pos)
            array.append(element)
            pos += offset

        return cls(array), pos


# Union type
RespType = Union[Integer, BulkString, SimpleString, SimpleError, Array]


def resp_type_from_bytes(data: bytes, pos: int = 0) -> tuple[RespType, int]:
    """
    Utility function that deserializes bytes to appropriate RespType.

    Args:
        data (bytes): The byte buffer to deserialize.
        pos (int, optional): The starting position in the byte buffer. Defaults to 0.

    Returns:
        tuple[RespType, int]: A tuple of deserialized `RespType` and the updated buffer position after parsing.

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
