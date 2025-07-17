from app.commands.base import RedisCommand
from app.commands.parser import CommandArgParser
from app.context import ExecutionContext
from app.resp import BulkString


class CommandEcho(RedisCommand):
    """Returns client-provided message.

    Syntax:
    ECHO message
    """

    args: dict = {}

    def __init__(self, args_list: list):
        parser = CommandArgParser()
        parser.add_argument("message", 0)
        self.args = parser.parse_args(args_list)

    def exec(self, ctx: ExecutionContext) -> bytes:
        return bytes(BulkString(self.args["message"]))
