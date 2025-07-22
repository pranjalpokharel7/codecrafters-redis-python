from app.commands.base import ExecutionResult, RedisCommand
from app.commands.parser import CommandArgParser
from app.context import ExecutionContext
from app.resp import BulkString
from app.resp.types.array import Array


class CommandReplConfGetACK(RedisCommand):
    """The REPLCONF GETACK is an internal command used to track offset numbers
    for synchronization between primary and replica. This is sent by the master
    to the replica.

    Syntax:
        REPLCONF GETACK *
    """

    args: dict
    write: bool = False

    def __init__(self, args_list: list[bytes]):
        parser = CommandArgParser()
        parser.add_argument("offset", 0)
        self.args = parser.parse_args(args_list)

    def exec(self, ctx: ExecutionContext, **kwargs) -> ExecutionResult:
        # hardcoded response for now
        current_offset = ctx.info.get_offset()
        return bytes(
            Array(
                [
                    BulkString(b"REPLCONF"),
                    BulkString(b"ACK"),
                    BulkString(f"{current_offset}".encode()),
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
