from app.commands.args.mapping import map_to_str_list
from app.commands.base import ExecutionResult, RedisCommand
from app.commands.decorators import queueable
from app.commands.args.parser import CommandArgParser
from app.context import ConnectionContext, ExecutionContext
from app.resp.types import BulkString
from app.resp.types.array import Array


class CommandInfo(RedisCommand):
    """The INFO command returns information and statistics about the server in
    a format that is simple to parse by computers and easy to read by humans.

    The optional parameter (section) can be used to select a specific section of information.
    Syntax:
        INFO [section [section ...]]
    """

    args: dict

    def __init__(self, args_list: list[bytes]):
        parser = CommandArgParser()
        parser.add_argument(
            "section",
            0,
            required=False,
            capture=True,
            map_fn=map_to_str_list,
        )
        self.args = parser.parse_args(args_list)

    @queueable
    def exec(
        self, exec_ctx: ExecutionContext, conn_ctx: ConnectionContext, **kwargs
    ) -> ExecutionResult:
        if section_names := self.args["section"]:
            sections = exec_ctx.info.get_sections_by_names(section_names)
        else:
            # when no section is provided as argument, simply return all sections
            sections = exec_ctx.info.get_all_sections()

        info = b"".join(sections.values())
        return bytes(BulkString(info))

    def __bytes__(self) -> bytes:
        array = [BulkString(b"INFO")]
        if isinstance(self.args["section"], list):
            for section_name in self.args["section"]:
                array.append(BulkString(section_name.encode()))
        return bytes(Array(array))
