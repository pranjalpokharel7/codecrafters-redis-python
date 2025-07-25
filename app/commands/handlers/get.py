from app.commands.base import ExecutionResult, RedisCommand
from app.commands.decorators import queueable
from app.commands.args.parser import CommandArgParser
from app.context import ConnectionContext, ExecutionContext
from app.resp.types import NIL, BulkString
from app.resp.types.array import Array
from app.storage.in_memory.errors import KeyDoesNotExist, KeyExpired


class CommandGet(RedisCommand):
    """Returns the string value of a key. If the key does not exist the special
    value nil is returned. An error is returned if the value stored at key is
    not a string, because GET only handles string values.

    Syntax:
      GET key
    """

    args: dict

    def __init__(self, args_list: list[bytes]):
        parser = CommandArgParser()
        parser.add_argument("key", 0)
        self.args = parser.parse_args(args_list)

    @queueable
    def exec(
        self, exec_ctx: ExecutionContext, conn_ctx: ConnectionContext, **kwargs
    ) -> ExecutionResult:
        key = self.args["key"]
        try:
            value = exec_ctx.storage.get(key)
            return bytes(BulkString(bytes(value)))
        except (KeyDoesNotExist, KeyExpired):
            return NIL

    def __bytes__(self) -> bytes:
        key = self.args["key"]
        return bytes(Array([BulkString(b"GET"), BulkString(key)]))
