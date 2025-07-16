from app.types import (
    Array,
    BulkString,
    Integer,
    SimpleError,
    SimpleString,
    resp_type_from_bytes,
)


def test_deserialize_simple_string():
    input = b"+OK\r\n"
    element, _ = resp_type_from_bytes(input)
    assert isinstance(element, SimpleString)
    assert element.value == b"OK"


def test_deserialize_simple_error():
    input = b"-Error\r\n"
    element, _ = resp_type_from_bytes(input)
    assert isinstance(element, SimpleError)
    assert element.value == b"Error"


def test_deserialize_integer():
    input = b":12345\r\n"
    element, _ = resp_type_from_bytes(input)
    assert isinstance(element, Integer)
    assert int(element.value) == 12345


def test_deserialize_bulk_string():
    input = b"$5\r\nhello\r\n"
    element, _ = resp_type_from_bytes(input)
    assert isinstance(element, BulkString)
    assert element.value == b"hello"


def test_deserialize_array():
    input_data = b"*7\r\n+Hello\r\n-World\r\n:100\r\n$4\r\ntest\r\n*2\r\n+Nested\r\n-Array\r\n+Another\r\n-Element\r\n"
    element, _ = resp_type_from_bytes(input_data)
    assert isinstance(element, Array)
    array = element.value
    assert len(array) == 7

    assert isinstance(array[0], SimpleString)
    assert array[0].value == b"Hello"

    assert isinstance(array[1], SimpleError)
    assert array[1].value == b"World"

    assert isinstance(array[2], Integer)
    assert array[2].value == b"100"

    assert isinstance(array[3], BulkString)
    assert array[3].value == b"test"

    assert isinstance(array[4], Array)  # Nested array not last
    nested = array[4].value
    assert len(nested) == 2
    assert isinstance(nested[0], SimpleString)
    assert nested[0].value == b"Nested"
    assert isinstance(nested[1], SimpleError)
    assert nested[1].value == b"Array"

    assert isinstance(array[5], SimpleString)
    assert array[5].value == b"Another"

    assert isinstance(array[6], SimpleError)
    assert array[6].value == b"Element"
