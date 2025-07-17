from time import time

from app.commands.base import ExecutionContext, RedisCommand
from app.commands.parser import CommandArgParser
from app.storage.in_memory.errors import KeyDoesNotExist
from app.resp.types import BulkString, NIL


class CommandGet(RedisCommand):
    """Returns the string value of a key. If the key does not exist the special
    value nil is returned. An error is returned if the value stored at key is
    not a string, because GET only handles string values.

    Syntax:
      GET key
    """

    args: dict = {}

    def __init__(self, args_list: list):
        parser = CommandArgParser()
        parser.add_argument("key", 0)
        self.args = parser.parse_args(args_list)

    def exec(self, ctx: ExecutionContext) -> bytes:
        key = self.args["key"]
        try:
            rv = ctx.storage.get(key)
            value, expiry = rv.value, rv.expiry

            if expiry and expiry < int(time() * 1000): # timestamp is stored in ms
                ctx.storage.remove(key) # remove expired key
                return NIL

            return bytes(BulkString(value))

        except KeyDoesNotExist:
            return NIL
