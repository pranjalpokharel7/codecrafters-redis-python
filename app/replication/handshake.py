"""This file will contain logic to perform initial handshake with the master as
a replica."""

import logging
import socket

from app.commands.base import RedisCommand
from app.commands.handlers.ping import CommandPing
from app.commands.handlers.psync import CommandPsync
from app.commands.handlers.replconf import CommandReplConf
from app.replication.errors import HandshakeFailed
from app.resp.types import SimpleString


class ReplicaHandshakeClient:
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

    def _send_command(self, command: RedisCommand) -> bytes:
        req = bytes(command)
        logging.info(f"sending command to master replica: {req!r}")
        self.sock.sendall(req)
        return self._recv_until_carriage_return()

    def _send_command_and_expect(self, command: RedisCommand, expected: bytes):
        response = self._send_command(command)
        if response != expected:
            raise HandshakeFailed(
                f"{command.name()} - expected {expected!r}, got {response!r}"
            )

    def _read_exact_length_and_advance(self, length: int) -> bytes:
        """Reads buffer up to specified length and advances buffer to start
        from the next character."""
        result = self.buf[:length]
        self.buf = self.buf[length:]
        return result

    def _recv_until_carriage_return(self) -> bytes:
        while True:
            chunk = self.sock.recv(1024 * 4)
            if not chunk:
                raise HandshakeFailed("connection closed unexpectedly")
            self.buf += chunk

            pos = self.buf.find(b"\r\n")
            if pos != -1:
                return self._read_exact_length_and_advance(pos + 2)

    def handshake(self) -> tuple[int, bytes]:
        """Establish handshake with master replica. Returns a tuple of the current offset
        of the master and the snapshot of the master's latest RDB."""
        # send PING
        self._send_command_and_expect(CommandPing([]), b"+PONG\r\n")

        # send REPLCONF messages
        self._send_command_and_expect(
            CommandReplConf([b"listening-port", str(self.listening_port).encode()]),
            b"+OK\r\n",
        )
        self._send_command_and_expect(
            CommandReplConf([b"capa", b"psync2"]),
            b"+OK\r\n",
        )

        # parse offset - "+FULLSYNC <replid> <master_offset>\r\n"
        info, pos = SimpleString.from_bytes(
            self._send_command(CommandPsync([b"?", b"-1"]))
        )
        master_replica_info = info.value.decode().split(" ")
        master_offset = int(master_replica_info[2])

        # parse rdb - $<rdb_length>\r\n<rdb>
        if self.buf.startswith(b"$"):
            # buffer already contains rdb contents
            pos = self.buf.find(b"\r\n")
            length_buffer = self._read_exact_length_and_advance(pos + 2)
        else:
            length_buffer = self._recv_until_carriage_return()

        # skip starting byte and trailing carriage return
        rdb_length = int(length_buffer[1:-2].decode())

        # read rdb up to rdb_length bytes
        master_rdb_snapshot = self._read_exact_length_and_advance(rdb_length)

        logging.info("received RDB file: completed handshake with master server")
        return master_offset, master_rdb_snapshot
