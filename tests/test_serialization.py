from app.types import (
    Integer,
    BulkString,
    SimpleString,
    SimpleError,
    Array,
)


def test_serialize_simple_string():
    value = b"OK"
    expected = b"+OK\r\n"
    result = bytes(SimpleString(value))
    assert result == expected


def test_serialize_simple_error():
    value = b"Error message"
    expected = b"-Error message\r\n"
    result = bytes(SimpleError(value))
    assert result == expected


def test_serialize_integer():
    value = b"12345"
    expected = b":12345\r\n"
    result = bytes(Integer(value))
    assert result == expected


def test_serialize_bulk_string():
    value = b"hello"
    expected = b"$5\r\nhello\r\n"
    result = bytes(BulkString(value))
    assert result == expected


def test_serialize_array():
    value = [
        SimpleString(b"Hello"),
        Integer(b"123"),
        BulkString(b"World"),
    ]
    expected = b"*3\r\n+Hello\r\n:123\r\n$5\r\nWorld\r\n"
    result = bytes(Array(value))
    assert result == expected
