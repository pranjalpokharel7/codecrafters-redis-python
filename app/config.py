from argparse import Namespace
from dataclasses import dataclass
from typing import Optional

from typing_extensions import Self


# TODO: read/write should be thread-safe
@dataclass
class Config:
    dir: Optional[str] = None
    dbfilename: Optional[str] = None
