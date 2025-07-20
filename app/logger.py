"""This file sets configuration for logging.

This is an anti-pattern as we are importing this module just to set
configuration. TODO: search for alternative to load logging config from
a file.
"""

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
