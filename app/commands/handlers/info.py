from app.commands.base import ExecutionResult, RedisCommand, queueable
from app.commands.parser import CommandArgParser
from app.context import ConnectionContext, ExecutionContext
from app.resp.types import BulkString


class CommandInfo(RedisCommand):
    """The INFO command returns information and statistics about the server in
    a format that is simple to parse by computers and easy to read by humans.

    The optional parameter (section) can be used to select a specific section of information.
    Syntax:
        INFO [section [section ...]]
    """

    args: dict
    write: bool = False

    def __init__(self, args_list: list[bytes]):
        parser = CommandArgParser()
        parser.add_argument(
            "section",
            0,
            required=False,
            capture=True,
            map_fn=lambda sections: [s.decode() for s in sections],
        )
        self.args = parser.parse_args(args_list)
    
    @queueable
    def exec(
        self, exec_ctx: ExecutionContext, conn_ctx: ConnectionContext, **kwargs
    ) -> ExecutionResult:
        if section_names := self.args["section"]:
            sections = exec_ctx.info.get_sections(section_names)
        else:
            # when no section is provided as argument, simply return all sections
            sections = exec_ctx.info.get_all_sections()

        info = b"".join(bytes(s) for s in sections.values())
        return bytes(BulkString(info))
