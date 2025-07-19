"""This file will contain logic to handle replica in slave mode.

Notes:
    - Slave replicas are for read only (write commands are disabled - SET??)
"""

import logging
import socket

from app.commands.base import RedisCommand
from app.commands.handlers.ping import CommandPing
from app.commands.handlers.psync import CommandPsync
from app.commands.handlers.replconf import CommandReplConf
from app.replication.errors import HandshakeFailed

log = logging.getLogger("app")


class ReplicaSlave:
    # host and port of the master replica
    host: str
    port: int

    # port we are listening to for incoming responses from master
    listening_port: int

    def __init__(self, host: str, port: int, listening_port: int):
        self.host = host
        self.port = port
        self.listening_port = listening_port

        # create a persistent TCP connection to master replica
        self._sock = socket.create_connection((host, port))

    def send_command(self, command: RedisCommand) -> bytes:
        req = bytes(command)
        log.info(f"sending command to master replica: {req!r}")
        self._sock.sendall(req)
        return self._recv_response()

    def _recv_response(self) -> bytes:
        buf = b""
        # should we just rely on recv working properly?
        while not buf.endswith(b"\r\n"):
            buf += self._sock.recv(1024)
        return buf

    def handshake(self):
        # send ping to master server
        res = self.send_command(CommandPing([]))
        if res != b"+PONG\r\n":
            raise HandshakeFailed(f"PING failed: {res!r}")

        # send REPLCONF messages
        res = self.send_command(
            CommandReplConf([b"listening-port", str(self.listening_port).encode()])
        )
        if res != b"+OK\r\n":
            raise HandshakeFailed(f"REPLCONF listening_port failed: {res!r}")

        res = self.send_command(CommandReplConf([b"capa", b"psync2"]))
        if res != b"+OK\r\n":
            raise HandshakeFailed(f"REPLCONF capa failed: {res!r}")

        # Since this is the first time the replica is connecting to the master,
        # replication ID will be ? (a question mark) and offset will be -1
        self.send_command(CommandPsync([b"?", b"-1"]))

        # skip handling response for now
        log.info("completed handshake with master server")
