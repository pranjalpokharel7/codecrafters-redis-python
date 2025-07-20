import logging
import threading
import socket

from app.commands.handlers.psync import CommandPsync
from app.context import ExecutionContext
from app.info.sections.info_replication import ReplicationRole
from app.logger import log
from app.resp.types.array import resp_type_from_bytes
from app.resp.types.simple_error import SimpleError
from app.replication.slave import ReplicaSlave
from app.utils.parse_command import parsed_input_to_command
from app.commands.errors import CommandEmpty, UnrecognizedCommand


MAX_BUF_SIZE = 512  # this should be a config parameter


def handle_connection(
    client_socket: socket.socket, ctx: ExecutionContext, reply: bool = True
):
    """
    reply: if set to False, the server will simply process the command and will not respond
    """
    # use hostname:port as unique id for socket (for now)
    uid = f"{client_socket.getpeername()[0]}:{client_socket.getpeername()[1]}"
    buf = b""
    while True:
        buf += client_socket.recv(MAX_BUF_SIZE)
        if not buf:  # empty buffer means client has disconnected
            ctx.pool.remove(uid)
            break

        # keep on processing while buffer is not empty, then only listen
        while buf != b"":
            try:
                parsed_input, pos = resp_type_from_bytes(buf)
            except Exception as e:
                client_socket.sendall(bytes(SimpleError(str(e).encode())))
                logging.error(str(e))
                continue

            # update position of buffer
            pos = min(
                len(buf), pos
            )  # pos can be the length of buffer i.e. all inputs have been processed
            buf = buf[pos:]

            if isinstance(parsed_input, SimpleError):
                # log client error and continue
                logging.error(parsed_input)
                continue
            
            try:
                command = parsed_input_to_command(parsed_input)
            except Exception as e:
                client_socket.sendall(bytes(SimpleError(str(e).encode())))
                logging.error(str(e))
                continue

            response = command.exec(ctx)

            # commands like psync return multiple responses
            # TODO: should we just configure all commands to return list?
            try:
                if reply:
                    if isinstance(response, list):
                        for res in response:
                            log.info(f"sending response: {res}")
                            client_socket.sendall(res)
                    else:
                        log.info(f"sending response: {response}")
                        client_socket.sendall(response)

            except Exception as e:
                # send error to client and close connection
                log.exception(e)
                client_socket.close()
                ctx.pool.remove(uid)
                break

            # if request is PSYNC, then it is a replication request
            # and so we add the replica connection to the connection pool
            # we don't store every other request since they're usually not persistent
            if ctx.info.server_role() == ReplicationRole.MASTER:
                if isinstance(command, CommandPsync):
                    logging.info(f"saving replica connection: {uid}")
                    ctx.pool.add(uid, client_socket)

                # if the command is marked as "sync" i.e. send to other replicas
                if command.sync:
                    # forward serialized input as data to other replicas
                    logging.info(f"sending {parsed_input} to replicas")
                    ctx.pool.propagate(bytes(parsed_input))


def handle_connection_to_master_replica(
    master_host: str,
    master_port: int,
    listening_port: int,
    execution_context: ExecutionContext,
):
    try:
        replica = ReplicaSlave(
            host=master_host,
            port=master_port,
            listening_port=listening_port,
        )
        replica.handshake()

        # all propagated commands will be listened to at this thread
        # handle client connection will take additional parameter - reply?
        threading.Thread(
            target=handle_connection, args=(replica.sock, execution_context, False)
        ).start()

    except Exception as e:
        log.error(f"failed to connect to master replica: {e}")
