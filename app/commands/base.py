"""This file defines the base class for redis commands."""

from abc import ABC, abstractmethod

from app.context import ConnectionContext, ExecutionContext
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
