from app.commands.base import ExecutionResult, RedisCommand
from app.commands.decorators import broadcast, queueable
from app.commands.handlers import CommandSet
from app.commands.args.parser import CommandArgParser
from app.context import ConnectionContext, ExecutionContext
from app.resp.types import Integer
from app.resp.types.array import Array
from app.resp.types.bulk_string import BulkString
from app.resp.types.simple_error import SimpleError
from app.storage.in_memory.errors import KeyDoesNotExist, KeyExpired
from app.storage.types import RedisValue


class CommandIncr(RedisCommand):
    """Returns the string value of a key. If the key does not exist the special
    value nil is returned. An error is returned if the value stored at key is
    not a string, because GET only handles string values.

    Syntax:
      INCR key
    """

    args: dict
    write: bool = True

    def __init__(self, args_list: list[bytes]):
        parser = CommandArgParser()
        parser.add_argument("key", 0)
        self.args = parser.parse_args(args_list)

    @broadcast
    @queueable
    def exec(
        self, exec_ctx: ExecutionContext, conn_ctx: ConnectionContext, **kwargs
    ) -> ExecutionResult:
        key = self.args["key"]
        try:
            value = exec_ctx.storage.update(key, _incr_value)
            return bytes(Integer(bytes(value)))

        except (KeyDoesNotExist, KeyExpired):
            # create a new key with integer value 1
            CommandSet([key, b"1"]).exec(exec_ctx, conn_ctx, **kwargs)
            return bytes(Integer(b"1"))

        except (ValueError, UnicodeDecodeError):
            return bytes(SimpleError(b"ERR value is not an integer or out of range"))

    def __bytes__(self) -> bytes:
        key = self.args["key"]
        return bytes(Array([BulkString(b"INCR"), BulkString(key)]))


def _incr_value(value: RedisValue) -> RedisValue:
    incr = int(value.raw_bytes.decode()) + 1
    value.raw_bytes = str(incr).encode()
    return value
