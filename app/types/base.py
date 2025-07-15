"""Contains core base classes for serialization and deserialization."""

from abc import ABC, abstractmethod

from typing_extensions import Self


class RESPType(ABC):
    """Base class that defines methods and attributes for a RESP Type
    object."""

    # starting byte for identifying the type
    start_byte: bytes = b""

    @classmethod
    def validate(cls, data: bytes):
        """Simple validation function for starting byte and overall binary
        string format."""
        if not cls.start_byte:
            raise Exception(f"start_byte not set for class {cls.__name__}")

        if not data.startswith(cls.start_byte) or not data.endswith(b"\r\n"):
            raise ValueError(f"Invalid byte format for {cls.__name__}")


class Serializable(ABC):
    """Base class for classes that require byte serialization."""

    @abstractmethod
    def __bytes__(self) -> bytes:
        raise NotImplementedError


class Deserializable(ABC):
    """Base class for classes that can be deserialized from bytes."""

    @classmethod
    @abstractmethod
    def from_bytes(cls, data: bytes) -> tuple[Self, int]:
        raise NotImplementedError
