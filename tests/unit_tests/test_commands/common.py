from app.commands.base import ExecutionResult
from app.config import Config
from app.context import ExecutionContext, ConnectionContext
from app.queue import TransactionQueue
from app.info.base import Info
from app.pool import ConnectionPool
from app.storage.in_memory import SimpleStorage
from app.storage.rdb import RDBManager
from app.commands import RedisCommand


def _test_execution_context():
    config = Config()
    storage = SimpleStorage()
    info = Info()
    pool = ConnectionPool()
    rdb = RDBManager()
    return ExecutionContext(storage, config, info, rdb, pool)


def _test_connection_context():
    uid = ""  # localhost:random port number?
    tx_queue = TransactionQueue()
    return ConnectionContext(uid, tx_queue)


class CommandTestBase:
    def setup_method(self):
        self.exec_ctx = _test_execution_context()
        self.conn_ctx = _test_connection_context()

    def execute_command(self, command: RedisCommand) -> ExecutionResult:
        return command.exec(self.exec_ctx, self.conn_ctx)
