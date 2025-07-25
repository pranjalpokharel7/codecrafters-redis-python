# Module - Commands

The command module includes all logic related to command definition, parsing and execution.

- `handlers` - This contains handlers to specific commands (for eg, command `ECHO` from the client is handled by `CommandEcho` in `handlers/echo.py`).
- `decorators.py` - As name suggests, decorators for command execution function.
- `base.py` - Defines the base class `RedisCommand` which defines the API exposed by all commands.

Additionally, the `args/` directory contains additional logic required to work with command arguments.
- `args/parser.py` - Argument parser for commands.
- `args/mapping.py` - Mapping functions that can be applied to individual command arguments to store them in transformed form (eg, converting argument in `bytes` to `int`).
