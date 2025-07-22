import logging
from time import time

from app.commands.base import ExecutionResult, RedisCommand
from app.commands.parser import CommandArgParser
from app.context import ExecutionContext
from app.resp.types import NIL
from app.resp.types.array import Array
from app.resp.types.bulk_string import BulkString
from app.resp.types.simple_string import SimpleString
from app.storage.in_memory.base import RedisValue


class CommandSet(RedisCommand):
    """Set key to hold the string value. If key already holds a value, it is
    overwritten, regardless of its type. If key doesn't exist previously, it is
    created and value is set. Any previous time to live associated with the key
    is discarded on successful SET operation.

    Syntax:
      SET key value [NX | XX] [GET] [EX seconds | PX milliseconds |
        EXAT unix-time-seconds | PXAT unix-time-milliseconds | KEEPTTL]

    For the purpose of this exercise, we will only incorporate the expiry argument
    (complicated to add nx and get since they are "more optional" than expiry)
    """

    args: dict = {}
    write: bool = True

    def __init__(self, args_list: list[bytes]):
        parser = CommandArgParser()
        parser.add_argument("key", 0)
        parser.add_argument("value", 1)
        parser.add_argument("expiry", 2, required=False, map_fn=lambda x: x.decode())
        parser.add_argument(
            "expiry_value", 3, required=False, map_fn=lambda x: x.decode()
        )

        self.args = parser.parse_args(args_list)

    def exec(self, ctx: ExecutionContext, **kwargs) -> ExecutionResult:
        key, value = self.args["key"], self.args["value"]
        expiry = self._calculate_key_expiry()
        try:
            ctx.storage.set(key, RedisValue(raw_bytes=value, expiry=expiry))
            return bytes(SimpleString(b"OK"))
        except Exception as e:  # currently an exception type is unknown
            logging.error(f"Command SET - {e}")
            return NIL

    def _calculate_key_expiry(self) -> int | None:
        # store expiry
        expiry: str | None = self.args["expiry"]
        expiry_value: str | None = self.args["expiry_value"]

        current_millis = lambda: int(time() * 1000)
        if expiry and expiry_value:
            match expiry.upper():
                case "EX":
                    return current_millis() + int(expiry_value) * 1000
                case "PX":
                    return current_millis() + int(expiry_value)
                case "EXAT":
                    return int(expiry_value) * 1000
                case "PXAT":
                    return int(expiry_value)
                case _:
                    return None
