import time

from app.commands import CommandGet, CommandSet
from tests.common import get_test_execution_context


def test_set_then_get_returns_value():
    ctx = get_test_execution_context()

    # SET key
    set_cmd = CommandSet([b"foo", b"bar"])
    set_result = set_cmd.exec(ctx)
    assert set_result == b"+OK\r\n"

    # GET key
    get_cmd = CommandGet([b"foo"])
    get_result = get_cmd.exec(ctx)
    assert get_result == b"$3\r\nbar\r\n"


def test_get_missing_key_returns_nil():
    ctx = get_test_execution_context()

    get_cmd = CommandGet([b"nope"])
    result = get_cmd.exec(ctx)
    assert result == b"$-1\r\n"


def test_set_with_expiry():
    ctx = get_test_execution_context()

    # SET key with PX 30 ms
    set_cmd = CommandSet([b"temp", b"value", b"PX", b"30"])
    set_result = set_cmd.exec(ctx)
    assert set_result == b"+OK\r\n"

    # key should return successfully before expiry
    get_cmd = CommandGet([b"temp"])
    get_result = get_cmd.exec(ctx)
    assert get_result == b"$5\r\nvalue\r\n"

    time.sleep(0.05)  # wait 50ms

    # key should be deleted by expiry
    get_cmd = CommandGet([b"temp"])
    get_result = get_cmd.exec(ctx)
    assert get_result == b"$-1\r\n"
