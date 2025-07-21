import logging
import socket

from app.commands.base import ExecutionResult
from app.commands.handlers.psync import CommandPsync
from app.commands.handlers.replconf import CommandReplConf
from app.context import ExecutionContext
from app.info.sections.info_replication import ReplicationRole
from app.resp.types.array import bytes_to_resp
from app.resp.types.simple_error import SimpleError
from app.utils.command_from_resp import command_from_resp_array

MAX_BUF_SIZE = 512  # this should be a config parameter


def _send_response(client_socket: socket.socket, response: ExecutionResult):
    """Helper function to send response to a client socket.

    Need an abstraction because we haven't finalized the exact response
    type for now.
    """
    # commands like psync return multiple responses
    if isinstance(response, list):
        for res in response:
            logging.info(f"sending response: {res}")
            client_socket.sendall(res)
    else:
        logging.info(f"sending response: {response}")
        client_socket.sendall(response)


def _process_and_update_buffer(
    buf: bytes,
    connection_uid: str,
    client_socket: socket.socket,
    ctx: ExecutionContext,
    replication_connection: bool = False,
) -> bytes:
    """Processes recv buffer and returns the updated buffer with remaining
    unparsed elements (if any)."""
    # keep on processing while buffer is not empty then return
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
            response = command.exec(ctx)
        except Exception as e:
            client_socket.sendall(bytes(SimpleError(str(e).encode())))
            logging.error(str(e))
            continue

        if not replication_connection or isinstance(command, CommandReplConf):
            _send_response(client_socket, response)

        # Only PSYNC requests need persistent connection tracking (replication setup).
        # Other commands are stateless and handled per-request.
        if ctx.info.server_role() == ReplicationRole.MASTER:
            if isinstance(command, CommandPsync):
                ctx.pool.add(connection_uid, client_socket)

            # if the command is marked as "sync" i.e. send to other replicas
            if command.sync:
                ctx.pool.propagate(bytes(resp_element))
        else:
            # update local offset i.e. number of bytes processed 
            # if this is master-replica connection
            if replication_connection:
                ctx.info.add_to_offset(pos)

    return buf


def handle_connection(
    client_socket: socket.socket,
    ctx: ExecutionContext,
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
    # use hostname:port as unique id for socket (for now)
    uid = f"{client_socket.getpeername()[0]}:{client_socket.getpeername()[1]}"
    buf = buf or b""

    # pre-process buffer if it isn't empty
    if buf:
        buf = _process_and_update_buffer(
            buf, uid, client_socket, ctx, replication_connection
        )

    try:
        while True:
            chunk = client_socket.recv(MAX_BUF_SIZE)
            if not chunk:  # empty buffer means client has disconnected
                break

            buf += chunk  # add received chunk to buffer

            # process and update buffer
            buf = _process_and_update_buffer(
                buf, uid, client_socket, ctx, replication_connection
            )

    except Exception as e:
        logging.exception(str(e))

    # close socket and remove from pool before exiting thread
    client_socket.close()
    ctx.pool.remove(uid)
