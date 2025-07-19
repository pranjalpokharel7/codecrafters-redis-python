import argparse


def _parse_replica_info(value: str) -> dict:
    parts = value.strip().split()
    if len(parts) != 2:
        raise argparse.ArgumentTypeError("replicaof must be '<HOST> <PORT>'")

    host, port = parts[0], parts[1]
    if not port.isdigit():
        raise argparse.ArgumentTypeError("port must be an integer")

    return {"host": host, "port": int(port)}


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
        type=_parse_replica_info,
        required=False,
        default=None,
        help="Specify master redis server to follow",
    )

    return parser
