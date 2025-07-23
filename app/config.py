from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    dir: Optional[str] = None
    dbfilename: Optional[str] = None
