import time
from app.commands import CommandGet, CommandSet
from tests.unit_tests.test_commands.common import CommandTestBase


class TestCommandSetGet(CommandTestBase):
    def test_set_then_get_returns_value(self):
        set_cmd = CommandSet([b"foo", b"bar"])
        set_result = self.execute_command(set_cmd)
        assert set_result == b"+OK\r\n"

        get_cmd = CommandGet([b"foo"])
        get_result = self.execute_command(get_cmd)
        assert get_result == b"$3\r\nbar\r\n"

    def test_get_missing_key_returns_nil(self):
        get_cmd = CommandGet([b"nope"])
        result = self.execute_command(get_cmd)
        assert result == b"$-1\r\n"

    def test_set_with_expiry(self):
        set_cmd = CommandSet([b"temp", b"value", b"PX", b"30"])
        set_result = self.execute_command(set_cmd)
        assert set_result == b"+OK\r\n"

        get_cmd = CommandGet([b"temp"])
        get_result = self.execute_command(get_cmd)
        assert get_result == b"$5\r\nvalue\r\n"

        time.sleep(0.05)  # wait 50ms

        get_cmd = CommandGet([b"temp"])
        get_result = self.execute_command(get_cmd)
        assert get_result == b"$-1\r\n"
