import base64
import logging
import os
from io import BytesIO

from app.storage.in_memory.base import RedisStorage
from app.storage.in_memory.errors import InvalidKeyFormat, InvalidValueFormat
from app.storage.rdb.parser import RDBParser


class RDBManager:
    """Class that encapsulates logic on storing, retrieving and manipulating
    database dumps in the form of RDB files. Doesn't maintain any internal state so is thread-safe.
    """

    def restore_from_file(
        self, path: str, storage: RedisStorage, read_threshold: int = 10 * 10 * 1024
    ):
        """Loads RDB file and restores server in-memory storage to the contents
        of the file.

        path: path to file
        storage: redis storage instance
        read_threshold: (optional) argument that sets the threshold for
                        reading entire file into memory (if file size is lesser than threshold)
                        or return a buffered reader to disk
        """

        try:
            file_size = os.path.getsize(path)
            with open(path, "rb") as f:
                if file_size <= read_threshold:
                    buf = f.read()
                    reader = BytesIO(buf)
                else:
                    reader = f

                logging.info(f"restoring storage from rdb backup file: {path}")
                parser = RDBParser()
                storage.restore(parser.parse(reader).db)

        except FileNotFoundError:
            # ignore if backup file doesn't exist
            pass

        except (InvalidKeyFormat, InvalidValueFormat):
            logging.error(
                "failed to restore snapshot because key-value contents are corrupted"
            )

    def restore_storage_from_snapshot(self, snapshot: bytes, storage: RedisStorage):
        """Restores contents of the storage from a snapshot."""
        try:
            logging.info("restoring storage from rdb snapshot")
            parser = RDBParser()
            reader = BytesIO(snapshot)
            storage.restore(parser.parse(reader).db)

        except (InvalidKeyFormat, InvalidValueFormat):
            logging.error(
                "failed to restore snapshot because key-value contents are corrupted"
            )

    def create_snapshot(self, storage: RedisStorage) -> bytes:
        """Creates a snapshot of RDB serialized file from current in-memory db
        contents.

        Currently returns a minimal placeholder RDB snapshot.
        """
        # TODO: create a serializer for RDB file format (could be a separate module)
        empty_rdb = "UkVESVMwMDEx+glyZWRpcy12ZXIFNy4yLjD6CnJlZGlzLWJpdHPAQPoFY3RpbWXCbQi8ZfoIdXNlZC1tZW3CsMQQAPoIYW9mLWJhc2XAAP/wbjv+wP9aog=="
        return base64.b64decode(empty_rdb)
