from dataclasses import asdict

from app.commands.arg_mapping import map_to_str_list
from app.commands.base import ExecutionResult, RedisCommand, queueable
from app.commands.parser import CommandArgParser
from app.context import ConnectionContext, ExecutionContext
from app.resp import Array, BulkString


class CommandConfigGet(RedisCommand):
    """The CONFIG GET command is used to read the configuration parameters of a
    running Redis server.

    Syntax:
    CONFIG GET parameter [parameter ...]
    """

    args: dict

    def __init__(self, args_list: list[bytes]):
        parser = CommandArgParser()
        parser.add_argument("parameter", 0, capture=True, map_fn=map_to_str_list)
        self.args = parser.parse_args(args_list)

    @queueable
    def exec(
        self, exec_ctx: ExecutionContext, conn_ctx: ConnectionContext, **kwargs
    ) -> ExecutionResult:
        array = []
        config_dict = asdict(exec_ctx.config)  # get config as dict for search

        for param_name in self.args["parameter"]:
            # it is not necessarily a one-one match since glob patterns are supported,
            # but it is out of scope for now
            if value := config_dict.get(param_name):
                array.extend(
                    [BulkString(param_name.encode()), BulkString(value.encode())]
                )

        return bytes(Array(value=array))

    def __bytes__(self) -> bytes:
        array = [BulkString(b"CONFIG"), BulkString(b"GET")]
        for param_name in self.args["parameter"]:
            array.append(BulkString(param_name.encode()))
        return bytes(Array(array))
