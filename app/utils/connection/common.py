import logging
import socket
import threading
from time import sleep, time

from app.commands.base import ExecutionResult, RedisCommand
from app.commands.handlers.discard import CommandDiscard
from app.commands.handlers.exec import CommandExec
from app.commands.handlers.multi import CommandMulti
from app.commands.handlers.psync import CommandPsync
from app.commands.handlers.replconf import CommandReplConf
from app.commands.handlers.wait import CommandWait
from app.context import ExecutionContext
from app.info.sections.info_replication import ReplicationRole
from app.resp.types.array import bytes_to_resp
from app.resp.types.integer import Integer
from app.resp.types.simple_error import SimpleError
from app.resp.types.simple_string import SimpleString
from app.transaction.queue import TransactionQueue
from app.utils.command_from_resp import command_from_resp_array

MAX_BUF_SIZE = 512  # this should be a config parameter


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


def _handle_wait(
    acks_required: int,
    timeout: int,  # in milliseconds
    ctx: ExecutionContext,
) -> int:
    master_offset = ctx.info.get_offset()
    start = int(
        time() * 1000
    )  # TODO: this start time needs to be from the start of receiving client socket

    # loop until waiting condition is fulfilled
    while True:
        if ctx.pool.acked_replicas(master_offset) >= acks_required:
            break

        current = int(time() * 1000)
        if current - start >= timeout:
            break

        # poll replicas for their latest offset
        threading.Thread(
            target=ctx.pool.send_getack,
            args=(master_offset,),
        ).start()

        sleep(0.02)  # throttle loop by 20ms

    count = ctx.pool.acked_replicas(master_offset)
    return count


def _handle_replication_logic(
    command: RedisCommand,
    propagation_bytes: bytes,
    connection_uid: str,
    client_socket: socket.socket,
    ctx: ExecutionContext,
    replication_connection: bool = False,
):
    offset = len(propagation_bytes)
    if ctx.info.server_role() == ReplicationRole.MASTER:
        if isinstance(command, CommandPsync):
            ctx.pool.add(connection_uid, client_socket)

        # wait execution of thread until we receive acknowledgement
        # from numreplicas or encounter timeout while waiting
        elif isinstance(command, CommandWait):
            acks_required, timeout = (
                command.args["numreplicas"],
                command.args["timeout"],
            )
            replicas_in_sync = _handle_wait(acks_required, timeout, ctx)
            _send_response(
                client_socket, bytes(Integer(str(replicas_in_sync).encode()))
            )

        # propagate write commands to other replicas
        elif command.write:
            # send messages to replicas in a background thread (non-blocking)
            threading.Thread(
                target=ctx.pool.propagate,
                args=(propagation_bytes,),
            ).start()

            # offset that increments for every byte of replication stream that it is produced to be sent to replicas
            logging.info(f"adding {offset} to master offset count")
            ctx.info.add_to_offset(offset)
    else:
        # for slave, update offset on write commands received from master
        # how do slaves update their offset?
        if replication_connection:
            ctx.info.add_to_offset(offset)


def _handle_transaction_logic(
    command: RedisCommand,
    connection_uid: str,
    tx_queue: TransactionQueue,
    ctx: ExecutionContext,
) -> bytes | None:
    if isinstance(command, CommandMulti):
        tx_queue.enter_transaction()

    elif isinstance(command, CommandExec):
        if not tx_queue.is_transaction_active():
            return bytes(SimpleError(b"ERR EXEC without MULTI"))

        else:
            results = []
            # also process all commands in the queue
            for command in tx_queue.get_command():
                extra_args = {"connection_uid": connection_uid}
                result = command.exec(ctx, **extra_args)

                # add result depending on it's type
                if isinstance(result, list):
                    results.extend(result)
                else:
                    if result:
                        results.append(result)

            tx_queue.exit_transaction()
            return f"*{len(results)}\r\n".encode() + b"".join(results)

    elif isinstance(command, CommandDiscard):
        if not tx_queue.is_transaction_active():
            return bytes(SimpleError(b"ERR EXEC without MULTI"))

        tx_queue.flush()
        tx_queue.exit_transaction()
        return bytes(SimpleString(b"OK"))


def _process_and_update_buffer(
    buf: bytes,
    connection_uid: str,
    tx_queue: TransactionQueue,
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

            if tx_queue.is_transaction_active():
                tx_queue.add_command(command)
                response = bytes(SimpleString(b"QUEUED"))
            else:
                extra_args = {"connection_uid": connection_uid}
                response = command.exec(ctx, **extra_args)
        except Exception as e:
            client_socket.sendall(bytes(SimpleError(str(e).encode())))
            logging.error(str(e))
            continue

        # update response as needed based on result of handling transaction logic
        if tx_result := _handle_transaction_logic(command, connection_uid, tx_queue, ctx):
            response = tx_result

        if not replication_connection or isinstance(command, CommandReplConf):
            _send_response(client_socket, response)

        # handle logic related to replication and server roles
        _handle_replication_logic(
            command,
            bytes(resp_element),
            connection_uid,
            client_socket,
            ctx,
            replication_connection,
        )

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
    logging.info(f"processing connection {uid}")

    buf = buf or b""
    tx_queue = TransactionQueue(uid)

    # pre-process buffer if it isn't empty before we listen for reads
    # (handle streaming incoming buffer)
    buf = _process_and_update_buffer(
        buf, uid, tx_queue, client_socket, ctx, replication_connection
    )

    try:
        while True:
            chunk = client_socket.recv(MAX_BUF_SIZE)
            if not chunk:  # empty buffer means client has disconnected
                break
            buf += chunk  # add received chunk to buffer

            # process and update buffer
            buf = _process_and_update_buffer(
                buf, uid, tx_queue, client_socket, ctx, replication_connection
            )

    except Exception as e:
        logging.exception(str(e))

    # close socket and remove from pool before exiting thread
    client_socket.close()
    ctx.pool.remove(uid)
