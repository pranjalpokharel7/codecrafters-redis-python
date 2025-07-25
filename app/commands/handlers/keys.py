from app.commands.base import ExecutionResult, RedisCommand
from app.commands.decorators import queueable
from app.commands.parser import CommandArgParser
from app.context import ConnectionContext, ExecutionContext
from app.resp.types import Array, BulkString


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

    args: dict

    def __init__(self, args_list: list[bytes]):
        parser = CommandArgParser()
        parser.add_argument("pattern", 0)
        self.args = parser.parse_args(args_list)

    @queueable
    def exec(
        self, exec_ctx: ExecutionContext, conn_ctx: ConnectionContext, **kwargs
    ) -> ExecutionResult:
        pattern = self.args["pattern"]
        keys = exec_ctx.storage.keys(pattern)
        return bytes(Array([BulkString(k) for k in keys]))

    def __bytes__(self) -> bytes:
        return bytes(
            Array(
                [
                    BulkString(b"KEYS"),
                    BulkString(self.args["pattern"]),
                ]
            )
        )
