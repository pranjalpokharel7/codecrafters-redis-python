from app.commands.base import ExecutionContext, ExecutionResult, RedisCommand
from app.commands.parser import CommandArgParser
from app.resp.types import NIL, BulkString
from app.storage.in_memory.errors import KeyDoesNotExist, KeyExpired


class CommandGet(RedisCommand):
    """Returns the string value of a key. If the key does not exist the special
    value nil is returned. An error is returned if the value stored at key is
    not a string, because GET only handles string values.

    Syntax:
      GET key
    """

    args: dict
    sync: bool = False

    def __init__(self, args_list: list[bytes]):
        parser = CommandArgParser()
        parser.add_argument("key", 0)
        self.args = parser.parse_args(args_list)

    def exec(self, ctx: ExecutionContext) -> ExecutionResult:
        key = self.args["key"]
        try:
            value = ctx.storage.get(key)
            return bytes(BulkString(bytes(value)))
        except (KeyDoesNotExist, KeyExpired):
            return NIL
