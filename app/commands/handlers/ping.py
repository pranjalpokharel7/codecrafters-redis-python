from app.commands.base import ExecutionResult, RedisCommand
from app.commands.decorators import queueable
from app.commands.parser import CommandArgParser
from app.context import ConnectionContext, ExecutionContext
from app.resp.types.array import Array
from app.resp.types.bulk_string import BulkString
from app.resp.types.simple_string import SimpleString


class CommandPing(RedisCommand):
    """Returns PONG if no argument is provided, otherwise return a copy of the
    argument as a bulk. Used to check the server's liveness response.

    Syntax:
    PING [message]
    """

    args: dict

    def __init__(self, args_list: list[bytes]):
        parser = CommandArgParser()
        parser.add_argument("message", 0, required=False, default=None)
        self.args = parser.parse_args(args_list)

    @queueable
    def exec(
        self, exec_ctx: ExecutionContext, conn_ctx: ConnectionContext, **kwargs
    ) -> ExecutionResult:
        if message := self.args["message"]:
            return bytes(BulkString(message))
        return bytes(SimpleString(b"PONG"))

    def __bytes__(self) -> bytes:
        array = [BulkString(b"PING")]
        if message := self.args["message"]:
            array.append(BulkString(message))
        return bytes(Array(array))
