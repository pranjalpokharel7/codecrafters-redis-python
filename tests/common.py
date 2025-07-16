from app.exec.base import ExecutionContext
from app.storage.in_memory import SimpleStorage


def get_test_execution_context():
    storage = SimpleStorage() 
    return ExecutionContext(storage)
