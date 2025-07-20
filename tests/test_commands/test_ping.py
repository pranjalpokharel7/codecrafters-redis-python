from app.commands import CommandPing
from tests.common import get_test_execution_context

def test_command_ping_default():
    cmd = CommandPing([])
    ctx = get_test_execution_context()
    result = cmd.exec(ctx)
    assert result == b"+PONG\r\n"

def test_command_ping_with_message():
    cmd = CommandPing([b"hello"])
    ctx = get_test_execution_context()
    result = cmd.exec(ctx)
    assert result == b"$5\r\nhello\r\n"
