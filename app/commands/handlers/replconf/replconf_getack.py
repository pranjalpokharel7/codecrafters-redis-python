from app.commands.base import ExecutionResult, RedisCommand
from app.commands.parser import CommandArgParser
from app.context import ExecutionContext
from app.resp import BulkString
from app.resp.types.array import Array


class CommandReplConfGetACK(RedisCommand):
    """The REPLCONF GETACK is an internal command used to track offset numbers
    for synchronization between primary and replica.

    Syntax:
        REPLCONF GETACK *
    """

    args: dict
    sync: bool = False

    def __init__(self, args_list: list[bytes]):
        parser = CommandArgParser()
        parser.add_argument("offset", 0)
        self.args = parser.parse_args(args_list)

    def exec(self, ctx: ExecutionContext) -> ExecutionResult:
        # hardcoded response for now
        return bytes(
            Array(
                [
                    BulkString(b"REPLCONF"),
                    BulkString(b"ACK"),
                    BulkString(b"0"),
                ]
            )
        )

    def __bytes__(self) -> bytes:
        array = [
            BulkString(b"REPLCONF"),
            BulkString(b"GETACK"),
            BulkString(b"*"),
        ]
        return bytes(Array(array))
