"""This file contains common functions to map command arguments to relevant
data types."""


def map_to_int(arg):
    return int(arg.decode())


def map_to_str(arg):
    return arg.decode()


def map_to_str_list(args):
    return [arg.decode() for arg in args]
