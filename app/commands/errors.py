"""This module defines all errors that are encountered during parsing and
execution of a redis command."""


class CommandError(Exception):
    pass


class CommandEmpty(CommandError):
    def __init__(self):
        super().__init__(f"empty command")


class MissingArgument(CommandError):
    def __init__(self, arg_name: str):
        super().__init__(f"missing argument: {arg_name}")


class UnrecognizedCommand(CommandError):
    def __init__(self, command_name: bytes) -> None:
        super().__init__(f"unrecognized command: {command_name}")
