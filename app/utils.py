from app.exec import NAME_TO_COMMANDS_MAP
from app.exec.base import RedisCommand
from app.exec.errors import CommandEmpty, UnrecognizedCommand
from app.types.resp import Array, RespElement


def parsed_input_to_command(parsed_input: RespElement) -> RedisCommand:
    """Creates a RedisCommand from the given RESP Element.

    Throws an exception if the element is not a RESP Array (for now,
    will be handled later if needed).
    """
    if not isinstance(parsed_input, Array):
        # unsure if there are future instances that will receive commands in non-array form
        raise Exception("invalid command format: expected serialized RESP array")

    array = parsed_input.value
    if len(array) < 1:
        raise CommandEmpty

    command_name = array[0].value
    subcommand_name = array[1].value if len(array) > 1 else b""

    # Reorder the checks for prefix matching if we don't have
    # compound and simple command names starting from the same prefix
    # (eg: ACL and ACL CAT - are these two different commands?)

    # Longest prefix match for compound commands
    compound_command_key = command_name + b" " + subcommand_name
    if compound_command_key in NAME_TO_COMMANDS_MAP:
        mapped_command = NAME_TO_COMMANDS_MAP[compound_command_key]
        return mapped_command([element.value for element in array[2:]])

    # Shorter prefix match for single command names
    elif command_name in NAME_TO_COMMANDS_MAP:
        mapped_command = NAME_TO_COMMANDS_MAP[command_name]
        return mapped_command([element.value for element in array[1:]])

    else:
        raise UnrecognizedCommand(command_name)
