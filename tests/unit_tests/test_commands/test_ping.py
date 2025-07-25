from app.commands import CommandPing
from tests.unit_tests.test_commands.common import CommandTestBase


class TestCommandPing(CommandTestBase):
    def test_command_ping_default(self):
        cmd = CommandPing([])
        result = self.execute_command(cmd)
        assert result == b"+PONG\r\n"

    def test_command_ping_with_message(self):
        cmd = CommandPing([b"hello"])
        result = self.execute_command(cmd)
        assert result == b"$5\r\nhello\r\n"
