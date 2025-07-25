import logging
import socket
import threading

from app.context import ConnectionContext, ExecutionContext
from app.connection.common import handle_connection


def accept_client_connections(
    server_socket: socket.socket, execution_context: ExecutionContext
):
    """Listens and accepts incoming client connections."""
    while True:
        client_socket, address = server_socket.accept()
        conn_ctx = ConnectionContext(sock=client_socket)
        logging.info(f"client connected: {address}")
        threading.Thread(
            target=handle_connection, args=(conn_ctx, execution_context)
        ).start()
