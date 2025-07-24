import logging
import socket

from app.commands.base import ExecutionResult, RedisCommand
from app.commands.handlers.psync import CommandPsync
from app.commands.handlers.replconf import CommandReplConf
from app.context import ConnectionContext, ExecutionContext
from app.info.sections.info_replication import ReplicationRole
from app.queue import TransactionQueue
from app.resp.types.array import bytes_to_resp
from app.resp.types.simple_error import SimpleError
from app.utils.command_from_resp import command_from_resp_array

MAX_BUF_SIZE = 512


def _send_response(client_socket: socket.socket, response: ExecutionResult):
    """Helper function to send response to a client socket."""
    # commands like psync return multiple responses
    if isinstance(response, list):
        for res in response:
            logging.info(f"sending response: {res}")
            client_socket.sendall(res)
    else:
        if response:
            logging.info(f"sending response: {response}")
            client_socket.sendall(response)


def _handle_replication_logic(
    command: RedisCommand,
    client_socket: socket.socket,
    conn_ctx: ConnectionContext,
    exec_ctx: ExecutionContext,
    replication_connection: bool = False,
):
    offset = len(bytes(command))
    if exec_ctx.info.server_role() == ReplicationRole.MASTER:
        # replicas make psync requests
        if isinstance(command, CommandPsync):
            exec_ctx.pool.add(conn_ctx.uid, client_socket)
            exec_ctx.info.add_to_connected_replica_count(1)
    else:
        # for slave, update offset on commands received from master
        if replication_connection:
            exec_ctx.info.add_to_offset(offset)


def _process_and_update_buffer(
    buf: bytes,
    client_socket: socket.socket,
    conn_ctx: ConnectionContext,
    exec_ctx: ExecutionContext,
    replication_connection: bool = False,
) -> bytes:
    """Processes recv buffer and returns the updated buffer with remaining
    unparsed elements (if any)."""
    while buf:
        try:
            resp_element, pos = bytes_to_resp(buf)
        except Exception as e:
            # if parsing fails, it can mean we haven't read the entire buffer yet
            client_socket.sendall(bytes(SimpleError(str(e).encode())))
            logging.error(str(e))
            break  # return since buffer is still expecting some input

        # update buffer
        buf = buf[pos:]

        # if the client sends error, simply log it and continue
        if isinstance(resp_element, SimpleError):
            logging.error(resp_element)
            continue

        # parse and execute command
        try:
            command = command_from_resp_array(resp_element)
            response = command.exec(exec_ctx, conn_ctx)
        except Exception as e:
            client_socket.sendall(bytes(SimpleError(str(e).encode())))
            logging.error(str(e))
            continue

        # replica do not reply on command execution to master
        # replconf is used during initial handshake -
        # except for getack and ack messages whose responses are sent
        if not replication_connection or isinstance(command, CommandReplConf):
            _send_response(client_socket, response)

        # handle logic related to replication and server roles
        _handle_replication_logic(
            command,
            client_socket,
            conn_ctx,
            exec_ctx,
            replication_connection,
        )

    return buf


def handle_connection(
    client_socket: socket.socket,
    exec_ctx: ExecutionContext,
    buf: bytes | None = None,
    replication_connection: bool = False,
):
    """Handles communication with a client socket once connection is
    established.

    buf: (optional) provide an initial buffer that contains unprocessed input
    replication_connection: if set to True, this is a replica-master connection
                            and is differently by the implementation as compared
                            to client connections
    """
    # hostname:port
    uid = f"{client_socket.getpeername()[0]}:{client_socket.getpeername()[1]}"
    tx_queue = TransactionQueue()
    conn_ctx = ConnectionContext(uid, tx_queue)
    logging.info(f"processing connection {uid}")

    # pre-process buffer if it isn't empty before we listen for reads
    # (handle streaming incoming buffer)
    buf = buf or b""
    buf = _process_and_update_buffer(
        buf, client_socket, conn_ctx, exec_ctx, replication_connection
    )

    try:
        while True:
            chunk = client_socket.recv(MAX_BUF_SIZE)
            if not chunk:  # empty buffer means client has disconnected
                break
            buf += chunk  # add received chunk to buffer
            buf = _process_and_update_buffer(
                buf, client_socket, conn_ctx, exec_ctx, replication_connection
            )

    except Exception as e:
        logging.exception(str(e))

    # close socket and remove from pool before exiting thread
    client_socket.close()

    if replication_connection:
        exec_ctx.pool.remove(uid)
        exec_ctx.info.add_to_connected_replica_count(-1)
