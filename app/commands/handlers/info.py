from dataclasses import asdict, dataclass, is_dataclass

from app.commands.base import ExecutionContext, RedisCommand
from app.commands.parser import CommandArgParser
from app.resp.types import NIL, BulkString
from app.resp.types.array import Array


class CommandInfo(RedisCommand):
    """The INFO command returns information and statistics about the server in
    a format that is simple to parse by computers and easy to read by humans.

    The optional parameter (section) can be used to select a specific section of information.
    Syntax:
        INFO [section [section ...]]
    """

    args: dict
    sync: bool = False

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

    def exec(self, ctx: ExecutionContext) -> bytes:
        if section_names := self.args["section"]:
            sections = ctx.info.get_sections(section_names)
        else:
            # when no section is provided as argument, simply return all sections
            sections = ctx.info.get_all_sections()

        info = b"".join(bytes(s) for s in sections.values())
        return bytes(BulkString(info))

