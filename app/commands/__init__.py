from app.commands.base import RedisCommand

from .handlers import *

# map from command name in bytes to their constructor class
NAME_TO_COMMANDS_MAP: dict[bytes, type[RedisCommand]] = {
    b"CONFIG": CommandConfig,
    b"ECHO": CommandEcho,
    b"GET": CommandGet,
    b"INCR": CommandIncr,
    b"INFO": CommandInfo,
    b"KEYS": CommandKeys,
    b"PING": CommandPing,
    b"PSYNC": CommandPsync,
    b"REPLCONF": CommandReplConf,
    b"SET": CommandSet,
    b"WAIT": CommandWait,
    b"MULTI": CommandMulti,
    b"EXEC": CommandExec,
}
