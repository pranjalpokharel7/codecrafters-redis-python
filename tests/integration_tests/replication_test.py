import subprocess
import time
import sys
import shutil

SERVER_CMD = "./your_program.sh"
MASTER_PORT = 6380
REPLICA_PORTS = [5000, 5001, 5002]  # spawn 3 replicas
REDIS_CLI = shutil.which("redis-cli")


def start_master():
    return subprocess.Popen(
        [SERVER_CMD, "--port", str(MASTER_PORT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def start_replica(port):
    return subprocess.Popen(
        [SERVER_CMD, "--port", str(port), "--replicaof", f"localhost {MASTER_PORT}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def stop_all(processes):
    for p in processes:
        p.terminate()
        p.wait()


def run_redis_command(port, cmd: list[str]) -> str:
    full_cmd = [REDIS_CLI, "-p", str(port)] + cmd
    return subprocess.check_output(full_cmd, text=True).strip()


def wait_for_replicas():
    """Give replicas time to connect & sync."""
    time.sleep(1)


def get_replication_offset(port: int) -> int:
    out = run_redis_command(port, ["REPLCONF", "GETACK", "*"])
    lines = [line.strip().strip('"') for line in out.splitlines() if line.strip()]
    return int(lines[-1])


def main():
    if REDIS_CLI is None:
        sys.exit("redis-cli not found in PATH")

    procs = []
    try:
        # Start master
        print("Starting master...")
        master_proc = start_master()
        procs.append(master_proc)
        time.sleep(1)

        # Start replicas
        for port in REPLICA_PORTS:
            print(f"Starting replica on port {port}...")
            proc = start_replica(port)
            procs.append(proc)

        wait_for_replicas()

        # Check handshake by sending PING
        for port in REPLICA_PORTS:
            out = run_redis_command(port, ["PING"])
            assert out == "PONG", f"Replica on port {port} failed handshake"

        print("All replicas connected successfully.")

        # Send SET to master
        run_redis_command(MASTER_PORT, ["SET", "sharedkey", "replication_test"])

        # Check replicas received the key
        for port in REPLICA_PORTS:
            val = run_redis_command(port, ["GET", "sharedkey"])
            assert val == "replication_test", (
                f"Replica on port {port} did not replicate key"
            )

        print("Replication of key verified on all replicas.")

        # Compare replication offsets using REPLCONF GETACK *
        master_offset = get_replication_offset(MASTER_PORT)
        for port in REPLICA_PORTS:
            replica_offset = get_replication_offset(port)
            assert replica_offset == master_offset, (
                f"Offset mismatch: master={master_offset}, replica={replica_offset} (port {port})"
            )

        print("Replication offsets match for all replicas.")

        print("=== REPLICATION TEST PASSED ===")

    finally:
        stop_all(procs)


if __name__ == "__main__":
    main()
