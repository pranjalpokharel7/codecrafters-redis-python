"""
Contains core base classes for serialization and deserialization.
"""

from typing_extensions import Self


class Serializable:
    """
    Base class for classes that require byte serialization.
    """

    def __bytes__(self) -> bytes:
        raise NotImplementedError


class ValidateBeforeDeserialization(type):
    """
    Metaclass for Deserializable (unused for now).

    When a class (that inherits from Deserializable) defines a `from_bytes(cls, data)` method,
    this metaclass wraps it so that `cls.validate(data)` is automatically called before any actual parsing.
    This ensures consistent precondition checks across all deserializable RESP types and avoids accidentally
    missing validation in implementation.
    """

    def __new__(mcs, name, bases, namespace):
        # Only wrap if from_bytes is explicitly defined
        if fn := namespace.get("from_bytes"):

            def wrapped(cls, data):
                cls.validate(data)  # always call validate first
                return fn.__get__(cls)(data)

            namespace["from_bytes"] = classmethod(wrapped)

        return super().__new__(mcs, name, bases, namespace)


class Deserializable:
    """
    Base class for classes that can be deserialized from bytes.
    """

    start_byte: bytes = b""

    @classmethod
    def validate(cls, data: bytes):
        if not cls.start_byte:
            raise Exception(f"start_byte not set for class {cls.__name__}")

        if not data.startswith(cls.start_byte) or not data.endswith(b"\r\n"):
            raise ValueError(f"Invalid byte format for {cls.__name__}")

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple[Self, int]:
        raise NotImplemented
