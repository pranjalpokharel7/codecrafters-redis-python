from app.config import Config
from app.context import ExecutionContext
from app.info.base import Info
from app.pool import ConnectionPool
from app.storage.in_memory import SimpleStorage
from app.storage.rdb import RDBManager


def get_test_execution_context():
    config = Config()
    storage = SimpleStorage()
    info = Info()
    pool = ConnectionPool()
    rdb = RDBManager()
    return ExecutionContext(storage, config, info, rdb, pool)
