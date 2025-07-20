from app.commands import CommandKeys
from app.storage.types import RedisValue
from tests.common import get_test_execution_context


def test_keys_exact_match():
    ctx = get_test_execution_context()
    ctx.storage.set(b"hello", RedisValue(raw_bytes=b"world"))
    cmd = CommandKeys([b"hello"])
    out = cmd.exec(ctx)
    assert b"hello" in out


def test_keys_wildcard_match():
    ctx = get_test_execution_context()
    ctx.storage.set(b"hello", RedisValue(b"1"))
    ctx.storage.set(b"hxllo", RedisValue(b"2"))
    ctx.storage.set(b"halo", RedisValue(b"3"))
    cmd = CommandKeys([b"h*llo"])
    out = cmd.exec(ctx)
    assert b"hello" in out
    assert b"hxllo" in out
    assert b"halo" not in out


def test_keys_character_set_match():
    ctx = get_test_execution_context()
    ctx.storage.set(b"hello", RedisValue(b"1"))
    ctx.storage.set(b"hallo", RedisValue(b"2"))
    ctx.storage.set(b"hillo", RedisValue(b"3"))
    cmd = CommandKeys([b"h[ae]llo"])
    out = cmd.exec(ctx)
    assert b"hello" in out
    assert b"hallo" in out
    assert b"hillo" not in out


def test_keys_range_match():
    ctx = get_test_execution_context()
    ctx.storage.set(b"hallo", RedisValue(b"1"))
    ctx.storage.set(b"hbllo", RedisValue(b"2"))
    ctx.storage.set(b"hcllo", RedisValue(b"3"))
    cmd = CommandKeys([b"h[a-b]llo"])
    out = cmd.exec(ctx)
    assert b"hallo" in out
    assert b"hbllo" in out
    assert b"hcllo" not in out


def test_keys_no_match():
    ctx = get_test_execution_context()
    ctx.storage.set(b"foo", RedisValue(b"1"))
    cmd = CommandKeys([b"bar*"])
    out = cmd.exec(ctx)
    assert out == b"*0\r\n"


# TODO: this test doesn't pass currently
# might have something to do with inconsistency
# of how we're constructing regex search
# def test_keys_negated_set_match():
#     ctx = get_test_execution_context()
#     ctx.storage.set(b"hello", RedisValue(b"1"))
#     ctx.storage.set(b"hallo", RedisValue(b"2"))
#     cmd = CommandKeys([b"h[^e]llo"])
#     out = cmd.exec(ctx)
#     assert b"hallo" in out
#     assert b"hello" not in out
