from app.commands.base import ExecutionResult, RedisCommand
from app.commands.parser import CommandArgParser
from app.commands.arg_mapping import map_to_int
from app.context import ExecutionContext, ConnectionContext
from app.resp import BulkString
from app.resp.types.array import Array


class CommandReplConfACK(RedisCommand):
    """The REPLCONF ACK is an internal command used by master to track which
    replicas got the last write. This is sent by each replica to the master on
    processing the most recent propagated command.

    Syntax:
        REPLCONF ACK <offset>
    """

    args: dict
    write: bool = False

    def __init__(self, args_list: list[bytes]):
        parser = CommandArgParser()
        parser.add_argument("offset", 0, map_fn=map_to_int)
        self.args = parser.parse_args(args_list)

    def exec(self, exec_ctx: ExecutionContext, conn_ctx: ConnectionContext, **kwargs) -> ExecutionResult:
        try:
            offset = self.args["offset"]
            exec_ctx.pool.update_last_ack_offset(conn_ctx.uid, offset)

        except Exception:
            pass  # ignore bad ACKs

        finally:
            return None

    def __bytes__(self) -> bytes:
        array = [
            BulkString(b"REPLCONF"),
            BulkString(b"GETACK"),
            BulkString(b"*"),
        ]
        return bytes(Array(array))
