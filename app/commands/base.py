"""This file defines the base class for redis commands."""

import threading
from abc import ABC, abstractmethod
from functools import wraps

from app.context import ConnectionContext, ExecutionContext
from app.info.sections.info_replication import ReplicationRole
from app.resp.types.simple_string import SimpleString

# type for result of executing a command
ExecutionResult = list[bytes] | bytes | None


class RedisCommand(ABC):
    """Base class that exposes API for command handlers."""

    args: dict  # arguments to the command, labeled as "argument name": "argument value"
    write: bool  # flag to denote whether the command makes write changes

    @abstractmethod
    def __init__(self, args_list: list[bytes]):
        raise NotImplementedError

    # should we always return a list of bytes though?
    # since we init using a list of bytes anyway?
    @abstractmethod
    def exec(
        self, exec_ctx: ExecutionContext, conn_ctx: ConnectionContext, **kwargs
    ) -> ExecutionResult:
        """Execute command by passing in a global execution context and a
        connection specific context."""
        raise NotImplementedError

    @abstractmethod
    def __bytes__(self) -> bytes:
        """Serialize command to bytes which can be used to communicate with
        another redis-server (for redis-client capabilities)."""
        raise NotImplementedError

    def name(self) -> str:
        """Returns command name.

        This is the class name of the command handler which is used to
        instantiate the command.
        """
        return self.__class__.__name__


def propagate(func):
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
                target=exec_ctx.pool.propagate,
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
