"""This file defines a redis command and it's execution environment.

From the redis docs -
"Clients send commands to a Redis server as an array of bulk strings.
The first (and sometimes also the second) bulk string in the array is the
command's name. Subsequent elements of the array are the arguments for the
command.".

Example: encoding of command - ECHO hey
*2\r\n$4\r\nECHO\r\n$3\r\nhey\r\n
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.storage.base import RedisStorage


@dataclass
class ExecutionContext:
    storage: RedisStorage


class RedisCommand(ABC):
    args: dict  # arguments to the command, labeled as "argument name": "argument value"

    @abstractmethod
    def __init__(self, args_list: list[bytes]):
        raise NotImplementedError

    def exec(self, ctx: ExecutionContext) -> bytes:
        """Execute command by passing in a global execution context."""
        raise NotImplementedError
