from dataclasses import dataclass
from typing import Optional


# TODO: read/write should be thread-safe
@dataclass
class Config:
    dir: Optional[str] = None
    dbfilename: Optional[str] = None
