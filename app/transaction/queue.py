import logging
import queue

from app.commands.base import RedisCommand


class TransactionQueue:
    """Queue commands for transactions.

    This is to be spawned for each thread so locking is not necessary
    (yet).
    """

    def __init__(self, uid: str) -> None:
        self._queue = queue.SimpleQueue()
        self._active = False
        self._uid = uid  # connection id to which the queue belongs to

    def is_transaction_active(self):
        return self._active

    def enter_transaction(self):
        logging.info("entering transaction")
        self._active = True

    def exit_transaction(self):
        logging.info("exiting transaction")
        self._active = False

    def add_command(self, command: RedisCommand):
        self._queue.put(command)

    def get_command(self):
        """Iterate through all commands currently in the queue."""
        while True:
            try:
                yield self._queue.get_nowait()
            except queue.Empty:
                break
