"""This file defines the base class for redis commands."""

from abc import ABC, abstractmethod

from app.context import ConnectionContext, ExecutionContext

# type for result of executing a command
ExecutionResult = list[bytes] | bytes | None


class RedisCommand(ABC):
    """Base class that exposes API for command handlers."""

    args: dict  # arguments to the command, labeled as "argument name": "argument value"

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
