from app.commands import CommandEcho
from tests.common import get_test_execution_context


def test_command_echo_returns_message():
    cmd = CommandEcho([b"hello"])
    ctx = get_test_execution_context()
    result = cmd.exec(ctx)
    assert result == b"$5\r\nhello\r\n"
