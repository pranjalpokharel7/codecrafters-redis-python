class CommandError(BaseException):
    pass


class CommandEmpty(CommandError):
    def __init__(self):
        super().__init__(f"empty command")


class MissingArgument(CommandError):
    def __init__(self, arg_name: str):
        super().__init__(f"missing argument: {arg_name}")


class CommandNameMismatch(CommandError):
    def __init__(self, command_name: str, provided_name: str):
        super().__init__(
            f"command name mismatch: expected={command_name}, got={provided_name}"
        )
