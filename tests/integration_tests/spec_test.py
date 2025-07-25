import argparse
import os
import shutil
import subprocess
import sys
import time

SERVER_CMD = "./your_program.sh"
REDIS_PORT = 6380  # use for tests
TESTS_DIR = "tests/integration_tests/specs"


def arg_parser():
    parser = argparse.ArgumentParser(
        description="Integration test for custom Redis server"
    )
    parser.add_argument(
        "--command-file", type=str, help="File containing commands and expected outputs"
    )
    return parser


def start_app():
    proc = subprocess.Popen(
        [SERVER_CMD, "--port", str(REDIS_PORT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(1)
    return proc


def stop_server(proc):
    proc.terminate()
    proc.wait()


def check_redis_cli_in_path():
    """Checks if redis-cli is found in system path.

    Exits if not found.
    """
    if shutil.which("redis-cli") is None:
        sys.exit("redis-cli not found in PATH")


def run_redis_command(cmd: list[str]) -> str:
    """
    Runs redis command and returns result.
    """
    full_cmd = ["redis-cli", "-p", str(REDIS_PORT)] + cmd
    return subprocess.check_output(full_cmd, text=True).strip()


def load_commands(file_path: str, delimiter="|") -> list[tuple[list[str], str]]:
    commands = []
    with open(file_path) as f:
        for line in f:
            if not line.strip():
                continue
            parts = [p.strip() for p in line.split(delimiter)]
            cmd = parts[0].split()
            expected = parts[1].replace("\\n", "\n") if len(parts) > 1 else None
            commands.append((cmd, expected))

    return commands


def run_test_file(file_path: str):
    print(f"\n=== Running test file: {file_path} ===")
    commands = load_commands(file_path)
    for cmd, expected in commands:
        output = run_redis_command(cmd)
        if expected is not None:
            assert output == expected, (
                f"Expected '{expected}' but got '{output}' for command {' '.join(cmd)}"
            )

    print(f"=== {file_path} PASSED ===")


def main():
    args = arg_parser().parse_args(sys.argv[1:])

    check_redis_cli_in_path()

    files = []
    if args.command_file:
        files = [args.command_file]
    else:
        if not os.path.isdir(TESTS_DIR):
            sys.exit(f"No command file provided and '{TESTS_DIR}' folder not found.")

        files = [
            os.path.join(TESTS_DIR, f)
            for f in os.listdir(TESTS_DIR)
            if f.endswith(".txt")
        ]

    if not files:
        sys.exit("No test files found.")

    proc = start_app()
    try:
        for file in files:
            run_test_file(file)
    finally:
        stop_server(proc)


if __name__ == "__main__":
    main()
