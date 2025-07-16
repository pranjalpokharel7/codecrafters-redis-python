# TODO: should we move this to the parser/ directory?

from dataclasses import dataclass
from typing import Any, Callable, Optional

from app.commands.errors import MissingArgument


@dataclass
class CommandArgument:
    """Represents a structure to work with Redis command arguments."""

    name: str  # name of the argument
    pos: int  # position of the argument
    required: bool  # whether the argument is required or optional
    default: Optional[Any] = None  # (optional) default value for the argument
    capture: bool = False  # capture trailing arguments (can make it similar to `nargs`)
    map_fn: Optional[Callable[[Any], Any]] = (
        None  # mapping function to be applied to argument
    )


class CommandArgParser:
    """Parser to parse command and it's arguments based on the definition
    provided."""

    args: list  # list of argument rules that define how arguments should be parsed

    def __init__(self):
        self.args = []

    def add_argument(
        self,
        name: str,
        pos: int,
        required: bool = True,
        default: Any = None,
        capture: bool = False,
        map_fn: Optional[Callable[[Any], Any]] = None,
    ):
        self.args.append(
            CommandArgument(
                name=name,
                pos=pos,
                required=required,
                default=default,
                map_fn=map_fn,
                capture=capture,
            )
        )

    def parse_args(self, args_list: list) -> dict:
        """Takes a list of arguments, validates them and labels each based on
        parsing rules."""
        parsed_args = {}

        for arg in self.args:
            # argument is provided if array is large enough to contain element at position
            if len(args_list) > arg.pos:
                if arg.capture:
                    # include all trailing arguments as argument value
                    value = args_list[arg.pos :]
                else:
                    value = args_list[arg.pos]

                # apply mapping function (if defined)
                if arg.map_fn:
                    value = arg.map_fn(value)

                parsed_args[arg.name] = value

            else:
                if arg.required:
                    raise MissingArgument(f"Missing at {arg.pos}: '{arg.name}'")
                else:
                    # use default value for optional args
                    parsed_args[arg.name] = arg.default

        return parsed_args
