"""
TODO: how do I propagate transactions to replicas? will this be our new test?
"""

from app.commands.base import ExecutionResult, RedisCommand
from app.commands.args.parser import CommandArgParser
from app.context import ConnectionContext, ExecutionContext
from app.resp.types.array import Array
from app.resp.types.simple_error import SimpleError
from app.resp.types.simple_string import SimpleString


class CommandDiscard(RedisCommand):
    """Flushes all previously queued commands in a transaction and restores the
    connection state to normal.

    Syntax:
        DISCARD
    """

    args: dict

    def __init__(self, args_list: list[bytes]):
        parser = CommandArgParser()
        self.args = parser.parse_args(args_list)

    def exec(
        self, exec_ctx: ExecutionContext, conn_ctx: ConnectionContext, **kwargs
    ) -> ExecutionResult:
        tx_queue = conn_ctx.tx_queue
        if not tx_queue.is_enabled():
            return bytes(SimpleError(b"ERR DISCARD without MULTI"))

        tx_queue.flush()
        tx_queue.disable()
        return bytes(SimpleString(b"OK"))

    def __bytes__(self) -> bytes:
        return bytes(Array([b"DISCARD"]))
