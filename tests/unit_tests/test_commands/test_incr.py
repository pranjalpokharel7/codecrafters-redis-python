import pytest
from app.commands import CommandIncr
from app.storage.types import RedisValue
from tests.unit_tests.test_commands.common import CommandTestBase


class TestCommandIncr(CommandTestBase):
    @pytest.mark.parametrize(
        "initial,expected",
        [
            (None, b":1\r\n"),
            (b"5", b":6\r\n"),
            (b"abc", b"-ERR value is not an integer or out of range\r\n"),
        ],
    )
    def test_incr_various(self, initial, expected):
        if initial is not None:
            self.exec_ctx.storage.set(b"counter", RedisValue(initial))
        cmd = CommandIncr([b"counter"])
        result = self.execute_command(cmd)
        assert result == expected
