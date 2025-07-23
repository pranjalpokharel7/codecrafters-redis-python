"""This file contains common functions to map command arguments to relevant
data types."""

map_to_int = lambda arg: int(arg.decode())
map_to_str = lambda arg: arg.decode()
map_to_str_list = lambda args: [arg.decode() for arg in args]
