from app.commands.base import ExecutionResult, RedisCommand, queueable
from app.commands.parser import CommandArgParser
from app.context import ConnectionContext, ExecutionContext
from app.resp import BulkString


class CommandEcho(RedisCommand):
    """Returns client-provided message.

    Syntax:
    ECHO message
    """

    args: dict
    write: bool = False

    def __init__(self, args_list: list[bytes]):
        parser = CommandArgParser()
        parser.add_argument("message", 0)
        self.args = parser.parse_args(args_list)

    @queueable
    def exec(
        self, exec_ctx: ExecutionContext, conn_ctx: ConnectionContext, **kwargs
    ) -> ExecutionResult:
        return bytes(BulkString(self.args["message"]))

    def __bytes__(self) -> bytes:
        return b"+ECHO\r\n"
