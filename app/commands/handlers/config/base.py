from app.commands.base import ExecutionResult, RedisCommand, queueable
from app.commands.errors import MissingSubcommand, UnrecognizedCommand
from app.commands.handlers.config.config_get import CommandConfigGet
from app.context import ConnectionContext, ExecutionContext


class CommandConfig(RedisCommand):
    """This handler routes execution through an appropriate handler based on
    the config subcommand provided.

    Syntax:
    CONFIG <subcommand>
    """

    args: dict
    write: bool = False
    active_sub_command: RedisCommand
    sub_commands: dict[bytes, type[RedisCommand]] = {b"GET": CommandConfigGet}

    def __init__(self, args_list: list[bytes]):
        if len(args_list) == 0:
            raise MissingSubcommand(b"CONFIG")

        sub_command_name = args_list[0]
        if sub_command := self.sub_commands.get(sub_command_name):
            self.active_sub_command = sub_command(args_list)
        else:
            raise UnrecognizedCommand(b"CONFIG " + sub_command_name)

    @queueable
    def exec(
        self, exec_ctx: ExecutionContext, conn_ctx: ConnectionContext, **kwargs
    ) -> ExecutionResult:
        return self.active_sub_command.exec(exec_ctx, conn_ctx, **kwargs)

    def __bytes__(self) -> bytes:
        return bytes(self.active_sub_command)
