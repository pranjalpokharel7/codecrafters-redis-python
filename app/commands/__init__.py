from app.commands.base import RedisCommand
from .handlers import *

# map from command name in bytes to their constructor class
NAME_TO_COMMANDS_MAP: dict[bytes, type[RedisCommand]] = {
    b"ECHO": CommandEcho,
    b"PING": CommandPing,
    b"GET": CommandGet,
    b"SET": CommandSet,
    b"KEYS": CommandKeys,
    b"INFO": CommandInfo,
    b"INCR": CommandIncr,

    # CONFIG
    b"CONFIG GET": CommandConfigGet,
}
