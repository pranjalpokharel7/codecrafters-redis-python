from dataclasses import asdict

from app.commands.base import ExecutionContext, RedisCommand
from app.commands.parser import CommandArgParser
from app.types import Array, BulkString


class CommandConfigGet(RedisCommand):
    """The CONFIG GET command is used to read the configuration parameters of a
    running Redis server.

    Syntax:
    CONFIG GET parameter [parameter ...]
    """

    args: dict = {}

    def __init__(self, args_list: list):
        parser = CommandArgParser()
        parser.add_argument(
            "parameter",
            0,
            capture=True,
            map_fn=lambda params: [
                p.decode() for p in params
            ],  # convert from bytes to utf-8
        )
        self.args = parser.parse_args(args_list)

    def exec(self, ctx: ExecutionContext) -> bytes:
        array = []
        config_dict = asdict(ctx.config) # get config as dict for search

        for param in self.args["parameter"]:
            # it is not necessarily a one-one match since glob patterns are supported, 
            # but it is out of scope for now
            value = config_dict.get(param)

            if value:  # only append if there is a match
                array.append(BulkString(param.encode()))
                array.append(BulkString(value.encode()))

        return bytes(Array(value=array))
