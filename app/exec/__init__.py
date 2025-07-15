from app.exec.base import RedisCommand
from .commands import *

# map command name in bytes to their command constructor class
NAME_TO_COMMANDS_MAP: dict[bytes, type[RedisCommand]] = {
    b"ECHO": CommandEcho,
    b"PING": CommandPing,
    b"GET": CommandGet,
    b"SET": CommandSet,
}
