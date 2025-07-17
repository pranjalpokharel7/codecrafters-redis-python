from app.commands.base import ExecutionContext, RedisCommand
from app.commands.parser import CommandArgParser
from app.types.resp import Array, BulkString


class CommandKeys(RedisCommand):
    """Returns all keys matching pattern.

    Supported glob-style patterns:

    h?llo matches hello, hallo and hxllo
    h*llo matches hllo and heeeello
    h[ae]llo matches hello and hallo, but not hillo
    h[^e]llo matches hallo, hbllo, ... but not hello
    h[a-b]llo matches hallo and hbllo

    Syntax:
      KEYS pattern
    """

    args: dict = {}

    def __init__(self, args_list: list):
        parser = CommandArgParser()
        parser.add_argument("pattern", 0)
        self.args = parser.parse_args(args_list)

    def exec(self, ctx: ExecutionContext) -> bytes:
        pattern = self.args["pattern"]
        keys = ctx.storage.keys(pattern)
        return bytes(Array([BulkString(k) for k in keys]))
