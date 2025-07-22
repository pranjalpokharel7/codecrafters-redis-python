from app.commands.base import ExecutionResult, RedisCommand
from app.commands.parser import CommandArgParser
from app.context import ExecutionContext


class CommandWait(RedisCommand):
    """This command blocks the current client until all the previous write
    commands are successfully transferred and acknowledged by at least the
    number of replicas you specify in the numreplicas argument. If the value
    you specify for the timeout argument (in milliseconds) is reached, the
    command returns even if the specified number of replicas were not yet
    reached.

    Syntax:
    """

    args: dict = {}
    write: bool = False 

    def __init__(self, args_list: list[bytes]):
        parser = CommandArgParser()
        parser.add_argument("numreplicas", 0, map_fn=lambda v: int(v.decode()))
        parser.add_argument("timeout", 1, map_fn=lambda v: int(v.decode()))
        self.args = parser.parse_args(args_list)

    def exec(self, ctx: ExecutionContext, **kwargs) -> ExecutionResult:
        # execution of wait command is handled at the master propagation section
        # the method is here just to maintain consistent API
        return None
