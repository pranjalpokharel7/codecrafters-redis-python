from app.commands import CommandInfo
from tests.common import get_test_execution_context

def test_info_replication_section():
    ctx = get_test_execution_context()
    cmd = CommandInfo([b"replication"])
    out = cmd.exec(ctx)
    assert isinstance(out, bytes)
    assert b"role:master" in out
