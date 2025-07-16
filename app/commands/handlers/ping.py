from app.context import ExecutionContext
from app.commands.base import RedisCommand
from app.commands.parser import CommandArgParser
from app.types.resp.bulk_string import BulkString


class CommandPing(RedisCommand):
    """Returns PONG if no argument is provided, otherwise return a copy of the
    argument as a bulk. Used to check the server's liveness response.

    Syntax:
    PING [message]
    """

    args: dict = {}

    def __init__(self, args_list: list):
        parser = CommandArgParser()
        parser.add_argument("message", 0, required=False, default=None)
        self.args = parser.parse_args(args_list)

    def exec(self, ctx: ExecutionContext) -> bytes:
        if message := self.args["message"]:
            return bytes(BulkString(message))
        return bytes(BulkString(b"PONG"))
