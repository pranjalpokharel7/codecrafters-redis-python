from app.commands.base import ExecutionResult, RedisCommand
from app.commands.parser import CommandArgParser
from app.context import ExecutionContext
from app.resp.types.simple_string import SimpleString


class CommandDiscard(RedisCommand):
    """Flushes all previously queued commands in a transaction and restores the
    connection state to normal.

    Syntax:
        DISCARD
    """

    args: dict
    write: bool = False  # is this writeable?

    def __init__(self, args_list: list[bytes]):
        parser = CommandArgParser()
        self.args = parser.parse_args(args_list)

    def exec(self, ctx: ExecutionContext, **kwargs) -> ExecutionResult:
        return bytes(SimpleString(b"OK"))
