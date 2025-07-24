import threading
from time import sleep, time

from app.commands.arg_mapping import map_to_int
from app.commands.base import ExecutionResult, RedisCommand
from app.commands.parser import CommandArgParser
from app.context import ConnectionContext, ExecutionContext
from app.resp.types.array import Array
from app.resp.types.bulk_string import BulkString
from app.resp.types.integer import Integer


class CommandWait(RedisCommand):
    """This command blocks the current client until all the previous write
    commands are successfully transferred and acknowledged by at least the
    number of replicas you specify in the numreplicas argument. If the value
    you specify for the timeout argument (in milliseconds) is reached, the
    command returns even if the specified number of replicas were not yet
    reached.

    Syntax:
        WAIT numreplicas timeout
    """

    args: dict = {}
    

    def __init__(self, args_list: list[bytes]):
        parser = CommandArgParser()
        parser.add_argument("numreplicas", 0, map_fn=map_to_int)
        parser.add_argument("timeout", 1, map_fn=map_to_int)
        self.args = parser.parse_args(args_list)

    def exec(
        self, exec_ctx: ExecutionContext, conn_ctx: ConnectionContext, **kwargs
    ) -> ExecutionResult:
        acks_required, timeout = (
            self.args["numreplicas"],
            self.args["timeout"],
        )
        replicas_in_sync = _count_replicas_in_sync(acks_required, timeout, exec_ctx)
        return bytes(Integer(str(replicas_in_sync).encode()))

    def __bytes__(self) -> bytes:
        numreplicas, timeout = (
            str(self.args["numreplicas"]).encode(),
            str(self.args["timeout"]).encode(),
        )
        return bytes(
            Array([BulkString(b"WAIT"), BulkString(numreplicas), BulkString(timeout)])
        )


def _count_replicas_in_sync(
    acks_required: int,
    timeout: int,  # in milliseconds
    ctx: ExecutionContext,
) -> int:
    master_offset = ctx.info.get_offset()
    start = int(time() * 1000)

    # loop until waiting condition is fulfilled
    while True:
        if ctx.pool.acked_replicas(master_offset) >= acks_required:
            break

        current = int(time() * 1000)
        if current - start >= timeout:
            break

        # poll replicas for their latest offset
        threading.Thread(
            target=ctx.pool.send_getack,
            args=(master_offset,),
        ).start()

        sleep(0.02)  # throttle loop by 20ms

    count = ctx.pool.acked_replicas(master_offset)
    return count
