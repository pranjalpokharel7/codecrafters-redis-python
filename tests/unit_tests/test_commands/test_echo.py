from app.commands import CommandEcho
from tests.unit_tests.test_commands.common import CommandTestBase


class TestEcho(CommandTestBase):
    def test_command_echo_returns_message(self):
        cmd = CommandEcho([b"hello"])
        result = self.execute_command(cmd)
        assert result == b"$5\r\nhello\r\n"
