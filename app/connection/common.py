import logging
import socket

from app.commands.base import ExecutionResult
from app.commands.handlers.replconf import CommandReplConf
from app.context import ConnectionContext, ExecutionContext
from app.info.sections.info_replication import ReplicationRole
from app.resp.types.array import bytes_to_resp
from app.resp.types.simple_error import SimpleError
from app.utils.command_from_resp import command_from_resp_array


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


def _process_and_update_buffer(
    buf: bytes, conn_ctx: ConnectionContext, exec_ctx: ExecutionContext
) -> bytes:
    """Processes recv buffer and returns the updated buffer with remaining
    unparsed elements (if any)."""
    while buf:
        try:
            resp_element, pos = bytes_to_resp(buf)
        except Exception as e:
            # if parsing fails, it can mean we haven't read the entire buffer yet
            conn_ctx.sock.sendall(bytes(SimpleError(str(e).encode())))
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
            conn_ctx.sock.sendall(bytes(SimpleError(str(e).encode())))
            logging.error(str(e))
            continue  # process next buffer stream

        # replicas do not reply on command execution to master
        # but do reply to master's replconf requests for GETACK
        if not conn_ctx.is_replica_connection or isinstance(command, CommandReplConf):
            _send_response(conn_ctx.sock, response)

        if (
            exec_ctx.info.server_role() == ReplicationRole.SLAVE
            and conn_ctx.is_replica_connection
        ):
            # for slave, update offset with number of bytes received
            # from master through the replication connection, pos is
            # the amount of byte processed for this iteration
            exec_ctx.info.add_to_offset(pos)

    return buf


def handle_connection(
    conn_ctx: ConnectionContext,
    exec_ctx: ExecutionContext,
    buf: bytes | None = None,
):
    """Handles communication with a client socket once connection is
    established.

    buf: (optional) provide an initial buffer that contains unprocessed input
    """
    # pre-process buffer if it isn't empty before we listen for reads
    buf = buf or b""
    buf = _process_and_update_buffer(buf, conn_ctx, exec_ctx)

    try:
        while True:
            chunk = conn_ctx.sock.recv(512)
            if not chunk:  # empty buffer means client has disconnected
                break
            buf += chunk  # add received chunk to buffer
            buf = _process_and_update_buffer(buf, conn_ctx, exec_ctx)

    except Exception as e:
        logging.exception(str(e))

    finally:
        # close socket and remove from pool before exiting thread
        conn_ctx.sock.close()

        if conn_ctx.is_replica_connection:
            exec_ctx.replica_pool.remove(conn_ctx.uid)
            exec_ctx.info.add_to_connected_replica_count(-1)
