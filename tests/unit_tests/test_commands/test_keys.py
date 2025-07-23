from app.commands import CommandKeys
from app.storage.types import RedisValue
from tests.unit_tests.test_commands.common import CommandTestBase

class TestCommandKeys(CommandTestBase):
    def setup_method(self):
        super().setup_method()
        self.exec_ctx.storage.restore({
            b"hello": RedisValue(b"1"),
            b"hxllo": RedisValue(b"2"),
            b"halo": RedisValue(b"3"),
            b"hallo": RedisValue(b"4"),
            b"hillo": RedisValue(b"5"),
            b"hbllo": RedisValue(b"6"),
            b"hcllo": RedisValue(b"7"),
            b"foo": RedisValue(b"8"),
        })

    def test_keys_exact_match(self):
        cmd = CommandKeys([b"hello"])
        result = self.execute_command(cmd)
        assert isinstance(result, bytes)
        for key in [b"hello"]:
            assert key in result

    def test_keys_wildcard_match(self):
        cmd = CommandKeys([b"h*llo"])
        result = self.execute_command(cmd)
        expected_present = [b"hello", b"hxllo"]
        expected_absent = [b"halo"]
        assert isinstance(result, bytes)
        for key in expected_present:
            assert key in result
        for key in expected_absent:
            assert key not in result

    def test_keys_character_set_match(self):
        cmd = CommandKeys([b"h[ae]llo"])
        result = self.execute_command(cmd)
        expected_present = [b"hello", b"hallo"]
        expected_absent = [b"hillo"]
        assert isinstance(result, bytes)
        for key in expected_present:
            assert key in result
        for key in expected_absent:
            assert key not in result

    def test_keys_range_match(self):
        cmd = CommandKeys([b"h[a-b]llo"])
        result = self.execute_command(cmd)
        expected_present = [b"hallo", b"hbllo"]
        expected_absent = [b"hcllo"]
        assert isinstance(result, bytes)
        for key in expected_present:
            assert key in result
        for key in expected_absent:
            assert key not in result

    def test_keys_no_match(self):
        cmd = CommandKeys([b"bar*"])
        result = self.execute_command(cmd)
        assert result == b"*0\r\n"
