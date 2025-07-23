import logging
import queue


class ToggledQueue:
    """Generic queue which can be toggled (enabled/disabled) as required.

    This is to be spawned for each thread so locking is not necessary
    (yet).
    """

    def __init__(self) -> None:
        self._queue = queue.SimpleQueue()
        self._enabled = False

    def is_enabled(self):
        return self._enabled

    def flush(self):
        """Remove all items from the queue."""
        while True:
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break

    def enable(self):
        logging.info("entering transaction")
        self._enabled = True

    def disable(self):
        logging.info("exiting transaction")
        self._enabled = False

    def put(self, item):
        """Put item in the queue, rejecting if queue is disabled."""
        if not self._enabled:
            raise RuntimeError("queue is disabled")  # custom error needed?
        self._queue.put(item)

    def get(self):
        """Iterate through all items currently in the queue."""
        while True:
            try:
                yield self._queue.get_nowait()
            except queue.Empty:
                break


# alias for toggled queue to be used for queuing commands for transactions
TransactionQueue = ToggledQueue
