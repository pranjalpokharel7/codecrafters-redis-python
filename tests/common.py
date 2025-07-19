from app.context import ExecutionContext
from app.config import Config
from app.info.base import Info
from app.storage.in_memory import SimpleStorage


def get_test_execution_context():
    config = Config()
    storage = SimpleStorage() 
    info = Info()
    return ExecutionContext(storage, config, info)
