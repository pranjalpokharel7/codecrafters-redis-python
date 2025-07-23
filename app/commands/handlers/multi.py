from app.commands.base import ExecutionResult, RedisCommand
from app.commands.parser import CommandArgParser
from app.context import ExecutionContext
from app.resp.types.simple_string import SimpleString


class CommandMulti(RedisCommand):
    """Marks the start of a transaction block. Subsequent commands will be
    queued for atomic execution using EXEC.

    Syntax:
        MULTI
    """

    args: dict
    write: bool = False # is this writeable?

    def __init__(self, args_list: list[bytes]):
        parser = CommandArgParser()
        self.args = parser.parse_args(args_list)

    def exec(self, ctx: ExecutionContext, **kwargs) -> ExecutionResult:
        return bytes(SimpleString(b"OK"))
