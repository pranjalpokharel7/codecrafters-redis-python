import logging
import os
from io import BytesIO

from app.storage.rdb.parser import RDBParser


def load_from_rdb_file(path: str, read_threshold: int = 10 * 10 * 1024) -> dict:
    """Loads RDB file and returns as dict for storage initialization.

    path: path to file
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

            return RDBParser(reader).db

    except FileNotFoundError:
        logging.info(f"rdb file {path} not found")
        # ignore if backup file doesn't exist
        return {}

