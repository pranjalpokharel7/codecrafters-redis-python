from app.commands import NAME_TO_COMMANDS_MAP
from app.commands.base import RedisCommand
from app.commands.errors import CommandEmpty, UnrecognizedCommand

from app.logger import log
from app.resp.types import Array, RespElement


MAX_BUF_SIZE = 512  # this should be a config parameter?


def parsed_input_to_command(parsed_input: RespElement) -> RedisCommand:
    """Creates a RedisCommand from the given RESP Element.

    Throws an exception if the element is not a RESP Array (for now,
    will be handled later if needed).
    """
    if not isinstance(parsed_input, Array):
        # unsure if there are future instances that will receive commands in non-array form
        raise ValueError("invalid command format: expected serialized RESP array")

    array = parsed_input.value
    if len(array) < 1:
        raise CommandEmpty

    # perform longer prefix match first if there are cases of common prefix
    # for eg, CMD and CMD RUN (both fictional commands, just for example)

    # shorter prefix match for single command names
    command_name = array[0].value
    if command_name in NAME_TO_COMMANDS_MAP:
        mapped_command = NAME_TO_COMMANDS_MAP[command_name]
        command_args = [element.value for element in array[1:]]
        log.info(f"received command: {command_name} {command_args}")
        return mapped_command(command_args)

    # longer prefix match for compound commands
    subcommand_name = array[1].value if len(array) > 1 else b""
    compound_command_key = command_name + b" " + subcommand_name
    if compound_command_key in NAME_TO_COMMANDS_MAP:
        mapped_command = NAME_TO_COMMANDS_MAP[compound_command_key]
        command_args = [element.value for element in array[2:]]
        log.info(f"received command: {command_name} {command_args}")
        return mapped_command(command_args)

    # command not recognized (or not implemented yet) internally
    raise UnrecognizedCommand(command_name)


