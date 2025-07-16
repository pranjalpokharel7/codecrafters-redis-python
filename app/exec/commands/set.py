from app.exec.base import ExecutionContext, RedisCommand
from app.exec.parser import CommandArgParser
from app.types.resp import Nil
from app.types.resp.bulk_string import BulkString
from app.types.resp.simple_string import SimpleString


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

    def __init__(self, args_list: list):
        parser = CommandArgParser()
        parser.add_argument("key", 0)
        parser.add_argument("value", 1)
        parser.add_argument("expiry", 2, required=False)
        parser.add_argument("expiry_value", 3, required=False)

        self.args = parser.parse_args(args_list)

    def exec(self, ctx: ExecutionContext) -> bytes:
        key, value = self.args["key"], self.args["value"]

        try:
            ctx.storage.set(key, value)
            return bytes(SimpleString(b"OK"))
        except Exception:  # currently an exception type is unknown
            # TODO: have a logger config to log exceptions
            return bytes(Nil)
