from app.exec.base import ExecutionContext
from app.exec.commands.echo import CommandEcho
from tests.common import get_test_execution_context


def test_command_echo_returns_message():
    cmd = CommandEcho([b"hello"])
    ctx = get_test_execution_context()
    result = cmd.exec(ctx)
    assert result == b"$5\r\nhello\r\n"


# TODO: need to test in actual redis server to see what is returned
# def test_command_echo_empty_message():
#     cmd = CommandEcho([b""])
#     ctx = get_test_execution_context()
#     result = cmd.exec(ctx)
#     assert result == b"$0\r\n\r\n"
