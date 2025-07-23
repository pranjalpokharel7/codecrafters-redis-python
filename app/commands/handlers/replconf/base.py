from app.commands.base import ExecutionResult, RedisCommand
from app.commands.handlers.replconf.replconf_getack import CommandReplConfGetACK
from app.commands.handlers.replconf.replconf_ack import CommandReplConfACK
from app.commands.parser import CommandArgParser
from app.context import ExecutionContext, ConnectionContext
from app.resp import BulkString
from app.resp.types.array import Array
from app.resp.types.simple_string import SimpleString


class CommandReplConf(RedisCommand):
    """The REPLCONF command is an internal command (it is not accessible by the
    external redis-client). It is used by a Redis master to configure a
    connected replica.

    Syntax:
        REPLCONF <conf-name> <conf-value>
    """

    args: dict
    write: bool = False

    def __init__(self, args_list: list[bytes]):
        parser = CommandArgParser()
        parser.add_argument("key", 0)
        parser.add_argument("value", 1)
        self.args = parser.parse_args(args_list)

    def exec(self, exec_ctx: ExecutionContext, conn_ctx: ConnectionContext, **kwargs) -> ExecutionResult:
        if self.args["key"].upper() == b"GETACK":
            return CommandReplConfGetACK([self.args["value"]]).exec(exec_ctx, conn_ctx, **kwargs)
        
        if self.args["key"].upper() == b"ACK":
            return CommandReplConfACK([self.args["value"]]).exec(exec_ctx, conn_ctx, **kwargs)

        return bytes(SimpleString(b"OK"))

    def __bytes__(self) -> bytes:
        key, value = self.args["key"], self.args["value"]
        array = [
            BulkString(b"REPLCONF"),
            BulkString(key),
            BulkString(value),
        ]
        return bytes(Array(array))
