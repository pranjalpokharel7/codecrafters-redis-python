from app.context import ExecutionContext
from app.commands.base import RedisCommand
from app.commands.parser import CommandArgParser
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
    sync: bool = False

    def __init__(self, args_list: list[bytes]):
        parser = CommandArgParser()
        parser.add_argument("message", 0, required=False, default=None)
        self.args = parser.parse_args(args_list)

    def exec(self, ctx: ExecutionContext) -> bytes:
        if message := self.args["message"]:
            return bytes(BulkString(message))
        return bytes(SimpleString(b"PONG"))

    def __bytes__(self) -> bytes:
        array = [BulkString(b"PING")]
        if message := self.args["message"]:
            array.append(BulkString(message))
        return bytes(Array(array))
