from app.commands.handlers import CommandConfig
from tests.unit_tests.test_commands.common import CommandTestBase

class TestCommandConfig(CommandTestBase):
    def test_config_get_single_param(self):
        self.exec_ctx.config.dir = "/data"
        cmd = CommandConfig([b"GET", b"dir"])
        result = self.execute_command(cmd)
        assert isinstance(result, bytes)
        for expected in [b"dir", b"/data"]:
            assert expected in result

    def test_config_get_multiple_params(self):
        self.exec_ctx.config.dir = "/data"
        self.exec_ctx.config.dbfilename = "dump.rdb"
        cmd = CommandConfig([b"GET", b"dir", b"dbfilename"])
        result = self.execute_command(cmd)
        assert isinstance(result, bytes)
        for expected in [b"dir", b"/data", b"dbfilename", b"dump.rdb"]:
            assert expected in result

    def test_config_get_nonexistent_param(self):
        cmd = CommandConfig([b"GET", b"unknown"])
        result = self.execute_command(cmd)
        assert result == b"*0\r\n"
