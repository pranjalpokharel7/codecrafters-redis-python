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
from app.replication.errors import HandshakeFailed


class ReplicaSlave:
    # host and port of the master replica
    master_host: str
    master_port: int

    # port used for logging purposes (out of scope for now)
    listening_port: int

    # persistent connection to master replica
    sock: socket.socket

    def __init__(self, master_host: str, master_port: int, listening_port: int):
        self.master_host = master_host
        self.master_port = master_port
        self.listening_port = listening_port

        # create a persistent TCP connection to master replica
        self.sock = socket.create_connection((master_host, master_port))

    def _send_command(self, command: RedisCommand) -> bytes:
        req = bytes(command)
        logging.info(f"sending command to master replica: {req!r}")
        self.sock.sendall(req)
        return self._recv_response()

    # TODO: each section should be parsed differently, compared to simply using recv
    def _recv_response(self) -> bytes:
        return self.sock.recv(1024 * 4)

    def handshake(self):
        """
        Establish handshake with master replica.
        """
        # send ping to master server
        res = self._send_command(CommandPing([]))
        if res != b"+PONG\r\n":
            raise HandshakeFailed(f"PING failed: {res!r}")

        # send REPLCONF messages
        res = self._send_command(
            CommandReplConf([b"listening-port", str(self.listening_port).encode()])
        )
        if res != b"+OK\r\n":
            raise HandshakeFailed(f"REPLCONF listening_port failed: {res!r}")

        res = self._send_command(CommandReplConf([b"capa", b"psync2"]))
        if res != b"+OK\r\n":
            raise HandshakeFailed(f"REPLCONF capa failed: {res!r}")

        # Since this is the first time the replica is connecting to the master,
        # replication ID will be ? (a question mark) and offset will be -1
        res = self._send_command(CommandPsync([b"?", b"-1"]))
        if res.endswith(b"\r\n"):
            # TODO check length from first response, read length then, use cr parser
            # this means we haven't received RDB file yet which doesn't end in carriage return - bit hackish for now but couldn't figure out the proper logic
            _rdb = self._recv_response()

        logging.info("received RDB file")

        # skip handling response for now
        logging.info("completed handshake with master server")
