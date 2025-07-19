import argparse


def get_arg_parser():
    parser = argparse.ArgumentParser(description="Redis clone server options")

    parser.add_argument(
        "--dir",
        type=str,
        required=False,
        default=None,
        help="Directory to store dump files",
    )

    parser.add_argument(
        "--dbfilename", type=str, required=False, default=None, help="RDB file name"
    )

    parser.add_argument(
        "--port",
        type=int,
        required=False,
        default=6379,
        help="Port to run the redis server on",
    )

    parser.add_argument(
        "--replicaof",
        type=str,
        required=False,
        default=None,
        help="Specify master redis server to follow",
    )

    return parser
