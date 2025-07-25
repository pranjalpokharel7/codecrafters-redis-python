from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """
    Parameters which are used to configure how the server is run/initialized.
    """

    dir: Optional[str] = None
    dbfilename: Optional[str] = None
