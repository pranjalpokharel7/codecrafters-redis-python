from app.commands.base import ExecutionResult, RedisCommand
from app.commands.parser import CommandArgParser
from app.context import ExecutionContext, ConnectionContext
from app.resp.types.array import Array
from app.resp.types.simple_error import SimpleError


class CommandExec(RedisCommand):
    """Executes all previously queued commands in a transaction and restores
    the connection state to normal.

    Syntax:
        EXEC
    """

    args: dict

    def __init__(self, args_list: list[bytes]):
        parser = CommandArgParser()
        self.args = parser.parse_args(args_list)

    def exec(self, exec_ctx: ExecutionContext, conn_ctx: ConnectionContext, **kwargs) -> ExecutionResult:
        tx_queue = conn_ctx.tx_queue
        if not tx_queue.is_enabled():
            return bytes(SimpleError(b"ERR EXEC without MULTI"))

        else:
            tx_queue.disable()
            results = []
            for command in tx_queue.get():
                result = command.exec(exec_ctx, conn_ctx, **kwargs)

                # add result depending on it's type
                if isinstance(result, list):
                    results.extend(result)
                else:
                    if result:
                        results.append(result)

            return f"*{len(results)}\r\n".encode() + b"".join(results)

    def __bytes__(self) -> bytes:
        return bytes(Array([b"EXEC"]))
