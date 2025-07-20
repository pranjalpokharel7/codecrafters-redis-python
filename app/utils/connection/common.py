import logging
import socket

from app.commands.handlers.psync import CommandPsync
from app.commands.base import ExecutionResult
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
    # TODO: should we just configure all commands to return list?
    if isinstance(response, list):
        for res in response:
            logging.info(f"sending response: {res}")
            client_socket.sendall(res)
    else:
        logging.info(f"sending response: {response}")
        client_socket.sendall(response)


def handle_connection(
    client_socket: socket.socket, ctx: ExecutionContext, respond: bool = True
):
    """Handles communication with a client socket once connection is
    established.

    respond: if set to False, the server will simply process the command and will not respond
             (False for communication between master-slave replica)
    """
    # use hostname:port as unique id for socket (for now)
    uid = f"{client_socket.getpeername()[0]}:{client_socket.getpeername()[1]}"
    buf = b""

    try:
        while True:
            buf += client_socket.recv(MAX_BUF_SIZE)
            if not buf:  # empty buffer means client has disconnected
                break

            # keep on processing while buffer is not empty, then only listen
            while buf:
                try:
                    resp_element, pos = bytes_to_resp(buf)
                except Exception as e:
                    # if parsing fails, it can mean we haven't read the entire buffer yet
                    client_socket.sendall(bytes(SimpleError(str(e).encode())))
                    logging.error(str(e))
                    break  # go to outer loop and wait on recv() call

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

                if respond:
                    _send_response(client_socket, response)


                # Only PSYNC requests need persistent connection tracking (replication setup).
                # Other commands are stateless and handled per-request.
                if ctx.info.server_role() == ReplicationRole.MASTER:
                    if isinstance(command, CommandPsync):
                        ctx.pool.add(uid, client_socket)

                    # if the command is marked as "sync" i.e. send to other replicas
                    if command.sync:
                        ctx.pool.propagate(bytes(resp_element))

    except Exception as e:
        logging.exception(str(e))

    # close socket and remove from pool before exiting thread
    client_socket.close()
    ctx.pool.remove(uid)

