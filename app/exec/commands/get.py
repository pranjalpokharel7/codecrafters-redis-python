from app.exec.base import ExecutionContext, RedisCommand
from app.exec.parser import CommandArgParser
from app.storage.errors import KeyDoesNotExist
from app.types.resp import BulkString, Nil


class CommandGet(RedisCommand):
    """Returns the string value of a key. If the key does not exist the special
    value nil is returned. An error is returned if the value stored at key is
    not a string, because GET only handles string values.

    Syntax:
      GET key
    """

    args: dict = {}

    def __init__(self, args_list: list):
        parser = CommandArgParser()
        parser.add_argument("key", 0)
        self.args = parser.parse_args(args_list)

    def exec(self, ctx: ExecutionContext) -> bytes:
        key = self.args["key"]
        try:
            value = ctx.storage.get(key)
            return bytes(BulkString(value))
        except KeyDoesNotExist:
            return bytes(Nil)
