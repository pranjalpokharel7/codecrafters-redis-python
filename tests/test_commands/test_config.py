from app.commands.handlers import CommandConfig
from tests.common import get_test_execution_context


def test_config_get_single_param():
    ctx = get_test_execution_context()
    ctx.config.dir = "/data"
    cmd = CommandConfig([b"GET", b"dir"])
    out = cmd.exec(ctx)
    assert b"dir" in out
    assert b"/data" in out


def test_config_get_multiple_params():
    ctx = get_test_execution_context()
    ctx.config.dir = "/data"
    ctx.config.dbfilename = "dump.rdb"
    cmd = CommandConfig([b"GET", b"dir", b"dbfilename"])
    out = cmd.exec(ctx)
    assert b"dir" in out
    assert b"/data" in out
    assert b"dbfilename" in out
    assert b"dump.rdb" in out


def test_config_get_nonexistent_param():
    ctx = get_test_execution_context()
    cmd = CommandConfig([b"GET", b"unknown"])
    out = cmd.exec(ctx)
    assert out == b"*0\r\n"
