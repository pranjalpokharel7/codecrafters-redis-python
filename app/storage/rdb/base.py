"""This file deals with loading from/saving to rdb file.

RDB files are used to backup contents of the in-memory database.
"""

import os
from io import BufferedReader, BytesIO

from app.storage.base import RedisStorage


class RDB:
    """This class provides interface to the db file."""

    path: str  # path to database
    read_threshold: int  # any file with size less than read_threshold will be read directly into memory for performance

    def __init__(self, path: str) -> None:
        self.path = path
        self.read_threshold = 10 * 1024 * 1024  # any RDB file less than

    # should this function also take execution context instead?
    def load(self):
        """Load and parse RDB file to in-memory database."""
        try:
            file_size = os.path.getsize(self.path)
            with open(self.path, "rb") as f:
                if file_size <= self.read_threshold:
                    reader = BytesIO(f.read())
                else:
                    reader = f

        except FileNotFoundError:
            # Note: The RDB file provided by --dir and --dbfilename might not exist.
            # If the file doesn't exist, your program must treat the database as empty.
            return {}

    # the following functions are out of scope currently...

    def save(self, storage: RedisStorage):
        """Save contents of the in-memory db to persistent file with
        appropriate format."""
        raise NotImplementedError

    # TODO: name `data` to something else?
    def encode(self, data: dict) -> bytes:
        """Encode contents of a RedisStorage to bytes."""
        raise NotImplementedError
