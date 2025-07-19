from app.commands.base import ExecutionContext, RedisCommand
from app.commands.parser import CommandArgParser
from app.commands.handlers import CommandSet
from app.resp.types.simple_error import SimpleError
from app.storage.in_memory.errors import KeyDoesNotExist, KeyExpired
from app.resp.types import Integer
from app.storage.types import RedisValue


class CommandIncr(RedisCommand):
    """Returns the string value of a key. If the key does not exist the special
    value nil is returned. An error is returned if the value stored at key is
    not a string, because GET only handles string values.

    Syntax:
      INCR key
    """

    args: dict
    sync: bool = True

    def _incr_value(self, value: RedisValue) -> RedisValue:
        incr = int(value.raw_bytes.decode()) + 1
        value.raw_bytes = bytes(incr)
        return value

    def __init__(self, args_list: list[bytes]):
        parser = CommandArgParser()
        parser.add_argument("key", 0)
        self.args = parser.parse_args(args_list)

    def exec(self, ctx: ExecutionContext) -> bytes:
        key = self.args["key"]
        try:
            value = ctx.storage.update(key, self._incr_value)
            return bytes(Integer(bytes(value)))

        except (KeyDoesNotExist, KeyExpired):
            # create a new key with integer value 1
            CommandSet([key, b"1"]).exec(ctx)
            return bytes(Integer(b"1"))
        
        except (ValueError, UnicodeDecodeError):
            return bytes(SimpleError(b"ERR value is not an integer or out of range"))
