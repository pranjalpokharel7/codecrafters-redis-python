"""This file defines the base class for redis commands."""

from abc import ABC, abstractmethod

from app.context import ExecutionContext

# type for result of executing a command
ExecutionResult = list[bytes] | bytes | None


class RedisCommand(ABC):
    """
    Base class that exposes API for command handlers.
    """
    args: dict  # arguments to the command, labeled as "argument name": "argument value"
    write: bool  # flag to denote whether the command makes write changes

    @abstractmethod
    def __init__(self, args_list: list[bytes]):
        raise NotImplementedError

    # should we always return a list of bytes though?
    # since we init using a list of bytes anyway?
    def exec(self, ctx: ExecutionContext, **kwargs) -> ExecutionResult:
        """Execute command by passing in a global execution context."""
        raise NotImplementedError

    def __bytes__(self) -> bytes:
        """Serialize command to bytes which can be used to communicate with
        another redis-server (for redis-client capabilities)."""
        raise NotImplementedError
