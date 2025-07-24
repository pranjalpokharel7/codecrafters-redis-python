from app.commands import CommandInfo
from tests.unit_tests.test_commands.common import CommandTestBase

class TestCommandInfo(CommandTestBase):
    def test_info_replication_section(self):
        cmd = CommandInfo([b"replication"])
        result = self.execute_command(cmd)
        assert isinstance(result, bytes)
        assert b"role:master" in result
        assert b"master_replid" in result
        assert b"master_repl_offset" in result
