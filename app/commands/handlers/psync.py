from typing import cast

from app.commands.base import ExecutionResult, RedisCommand
from app.commands.parser import CommandArgParser
from app.context import ConnectionContext, ExecutionContext
from app.info.sections.info_replication import InfoReplication
from app.resp import BulkString
from app.resp.types.array import Array
from app.resp.types.simple_string import SimpleString


class CommandPsync(RedisCommand):
    """The PSYNC command is called by Redis replicas for initiating a
    replication stream from the master.

    Syntax:
        PSYNC replicationid offset
    """

    args: dict

    def __init__(self, args_list: list[bytes]):
        parser = CommandArgParser()
        parser.add_argument("replicationid", 0)
        parser.add_argument("offset", 1)
        self.args = parser.parse_args(args_list)

    def exec(
        self, exec_ctx: ExecutionContext, conn_ctx: ConnectionContext, **kwargs
    ) -> ExecutionResult:
        replication = cast(
            InfoReplication, exec_ctx.info._get_section_by_name("replication")
        )
        ack = bytes(
            SimpleString(
                f"FULLRESYNC {replication.master_replid} {replication.master_repl_offset}".encode()
            )
        )
        snapshot = exec_ctx.rdb.create_snapshot(exec_ctx.storage)
        db = f"${len(snapshot)}\r\n".encode() + snapshot

        # add connection to pool since only replicas send psync requests
        exec_ctx.replica_pool.add(conn_ctx.uid, conn_ctx.sock)
        exec_ctx.info.add_to_connected_replica_count(1)

        return [ack, db]

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
