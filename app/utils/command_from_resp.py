import logging

from app.commands import NAME_TO_COMMANDS_MAP
from app.commands.base import RedisCommand
from app.commands.errors import CommandEmpty, UnrecognizedCommand

from app.resp.types import Array, RespElement


def command_from_resp_array(parsed_input: RespElement) -> RedisCommand:
    """Parse a RESP array and return a corresponding RedisCommand instance.

    Raises:
        ValueError: If the input is not a RESP array.
        CommandEmpty: If the array is empty.
        UnrecognizedCommand: If the command name is not recognized.
    """
    if not isinstance(parsed_input, Array):
        # unsure if there are future instances that will receive commands in non-array form
        raise ValueError("invalid command format: expected serialized RESP array")

    array = parsed_input.value
    if len(array) < 1:
        raise CommandEmpty

    command_name = array[0].value.upper()
    if command := NAME_TO_COMMANDS_MAP.get(command_name):
        command_args = [element.value for element in array[1:]]
        logging.info(f"received command: {command_name} with args {command_args}")
        return command(command_args)

    # command not recognized (or not implemented yet) internally
    raise UnrecognizedCommand(command_name)
