from .array import Array, RespElement, bytes_to_resp
from .bulk_string import BulkString
from .integer import Integer
from .simple_error import SimpleError
from .simple_string import SimpleString

# type nil/null is simply an empty bulk string
NIL = bytes(BulkString(b""))

__all__ = [
    "Array",
    "RespElement",
    "bytes_to_resp",
    "BulkString",
    "SimpleError",
    "SimpleString",
    "Integer",
    "NIL",
]
