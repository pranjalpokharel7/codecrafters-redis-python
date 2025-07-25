from unittest.mock import MagicMock

from app.commands import RedisCommand
from app.commands.base import ExecutionResult
from app.config import Config
from app.context import ConnectionContext, ExecutionContext
from app.info.base import Info
from app.replica.pool import ReplicaConnectionPool
from app.storage.in_memory import SimpleStorage
from app.storage.rdb import RDBManager


def mock_socket():
    """Returns a mock socket for testing.

    Note: Only supports the getpeername() method for now since it is
    required for connection context to be initialized. Add other methods
    in the implementation as necessary.
    """
    mock_sock = MagicMock()
    mock_sock.getpeername.return_value = ("127.0.0.1", 12345)
    return mock_sock


def _test_execution_context():
    config = Config()
    storage = SimpleStorage()
    info = Info()
    pool = ReplicaConnectionPool()
    rdb = RDBManager()
    return ExecutionContext(storage, config, info, rdb, pool)


def _test_connection_context():
    return ConnectionContext(mock_socket())


class CommandTestBase:
    def setup_method(self):
        self.exec_ctx = _test_execution_context()
        self.conn_ctx = _test_connection_context()

    def execute_command(self, command: RedisCommand) -> ExecutionResult:
        return command.exec(self.exec_ctx, self.conn_ctx)
