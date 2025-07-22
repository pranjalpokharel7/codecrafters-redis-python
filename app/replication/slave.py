"""This file will contain logic to handle replica in slave mode.

Notes:
    - Slave replicas are for read only
"""

import logging
import socket

from app.commands.base import RedisCommand
from app.commands.handlers.ping import CommandPing
from app.commands.handlers.psync import CommandPsync
from app.commands.handlers.replconf import CommandReplConf
from app.context import ExecutionContext
from app.replication.errors import HandshakeFailed


class ReplicaSlave:
    # host and port of the master replica
    master_host: str
    master_port: int

    # port used for logging purposes (out of scope for now)
    listening_port: int

    # persistent connection to master replica
    sock: socket.socket

    # internal buffer to parse incoming connections
    buf: bytes

    def __init__(self, master_host: str, master_port: int, listening_port: int):
        self.master_host = master_host
        self.master_port = master_port
        self.listening_port = listening_port
        self.buf = b""

        # create a persistent TCP connection to master replica
        self.sock = socket.create_connection((master_host, master_port))

    def _assert_response(self, received: bytes, expected: bytes):
        if received != expected:
            raise HandshakeFailed(f"Handshake failed: {received!r}")

    def _send_command(self, command: RedisCommand) -> bytes:
        req = bytes(command)
        logging.info(f"sending command to master replica: {req!r}")
        self.sock.sendall(req)
        return self._recv_response()

    def _read_buffer_length_and_advance(self, length: int) -> bytes:
        """Reads buffer up to specified length and advances buffer to start
        from the next character."""
        result = self.buf[:length]
        self.buf = self.buf[length:]
        return result

    # TODO: each section should be parsed differently, compared to simply using recv
    def _recv_response(self) -> bytes:
        while True:
            chunk = self.sock.recv(1024 * 4)
            if not chunk:
                raise HandshakeFailed("connection closed unexpectedly")

            self.buf += chunk
            pos = self.buf.find(b"\r\n")
            if pos != -1:
                return self._read_buffer_length_and_advance(pos + 2)

    def handshake(self, ctx: ExecutionContext):
        """Establish handshake with master replica."""
        # send ping to master server
        res = self._send_command(CommandPing([]))
        self._assert_response(res, b"+PONG\r\n")

        # send REPLCONF messages
        res = self._send_command(
            CommandReplConf([b"listening-port", str(self.listening_port).encode()])
        )
        self._assert_response(res, b"+OK\r\n")

        res = self._send_command(CommandReplConf([b"capa", b"psync2"]))
        self._assert_response(res, b"+OK\r\n")

        # Since this is the first time the replica is connecting to the master,
        # replication ID will be ? (a question mark) and offset will be -1
        res = self._send_command(CommandPsync([b"?", b"-1"]))
        # TODO: Huge todo - update client offset at this stage

        if self.buf.startswith(b"$"):  # buffer already contains rdb contents
            pos = self.buf.find(b"\r\n")
            length_buffer = self._read_buffer_length_and_advance(pos + 2)
        else:
            length_buffer = self._recv_response()

        # skip starting byte and trailing carriage return
        rdb_size = int(length_buffer[1:-2].decode())
        rdb_buffer = self._read_buffer_length_and_advance(rdb_size)
        ctx.rdb.restore_from_snapshot(rdb_buffer, ctx.storage)

        logging.info(
            "received and processed RDB file: completed handshake with master server"
        )
