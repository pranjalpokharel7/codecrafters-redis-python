from app.commands.base import RedisCommand
from app.commands.parser import CommandArgParser
from app.context import ExecutionContext
from app.resp import BulkString
from app.resp.types.array import Array


class CommandPsync(RedisCommand):
    """The PSYNC command is called by Redis replicas for initiating a
    replication stream from the master.

    Syntax:
        PSYNC replicationid offset
    """

    args: dict = {}

    def __init__(self, args_list: list[bytes]):
        parser = CommandArgParser()
        parser.add_argument("replicationid", 0)
        parser.add_argument("offset", 1)
        self.args = parser.parse_args(args_list)

    def exec(self, ctx: ExecutionContext) -> bytes:
        # server side response for psync
        raise NotImplementedError

    def __bytes__(self) -> bytes:
        # client side request for psync
        return bytes(
            Array(
                [
                    BulkString(b"PSYNC"),
                    BulkString(self.args["replicationid"]),
                    BulkString(self.args["offset"]),
                ]
            )
        )
