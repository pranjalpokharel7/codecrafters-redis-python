from app.exec.commands.set import CommandSet
from app.exec.commands.get import CommandGet
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
