from .array import Array, RespElement, resp_type_from_bytes
from .bulk_string import BulkString
from .integer import Integer
from .simple_error import SimpleError
from .simple_string import SimpleString

# type nil/null is simply an empty bulk string
NIL = bytes(BulkString(b""))
