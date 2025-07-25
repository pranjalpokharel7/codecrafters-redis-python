import threading
from functools import wraps

from app.commands.base import ExecutionResult
from app.context import ConnectionContext, ExecutionContext
from app.info.sections.info_replication import ReplicationRole
from app.resp.types.simple_string import SimpleString


def broadcast(func):
    """Decorator to the command execution method exec() which propagates the
    command (if operating as master replica) to other replicas post execution.

    Note that the command which uses this decorator must also implement
    the __bytes__ method.
    """

    @wraps(func)
    def wrapper(
        self, exec_ctx: ExecutionContext, conn_ctx: ConnectionContext, **kwargs
    ) -> ExecutionResult:
        result = func(self, exec_ctx, conn_ctx, **kwargs)
        if exec_ctx.info.server_role() == ReplicationRole.MASTER:
            replication_payload = bytes(self)

            # send messages to replicas in a background thread (non-blocking)
            threading.Thread(
                target=exec_ctx.pool.broadcast_to_all_connections,
                args=(replication_payload,),
            ).start()

            # offset that increments for every byte of replication
            # that is sent to replicas
            exec_ctx.info.add_to_offset(len(replication_payload))
        return result

    return wrapper


def queueable(func):
    """Decorator to command execution method exec() for commands which can be
    queued in a transaction.

    Expected that the transaction queue (tx_queue) is passed as kwargs
    for execution commands that can be queued.
    """

    def exec_wrapper(
        self, exec_ctx: ExecutionContext, conn_ctx: ConnectionContext, **kwargs
    ):
        if conn_ctx.tx_queue.is_enabled():
            conn_ctx.tx_queue.put(self)
            return bytes(SimpleString(b"QUEUED"))
        return func(self, exec_ctx, conn_ctx, **kwargs)

    return exec_wrapper
