import socket  # noqa: F401

MAX_BUF_SIZE = 512


def readall(connection: socket.socket):
    """
    This readall method needs to handle cases when not all bytes are read (edge cases).
    """
    return connection.recv(MAX_BUF_SIZE)


def handle_connection(connection: socket.socket):
    while True:
        buf = connection.recv(MAX_BUF_SIZE)
        if not buf:  # empty buffer means client has disconnected
            break

        connection.sendall(b"+PONG\r\n")


def main():
    print("Logs from your program will appear here!")
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)

    while True:
        connection, _ = server_socket.accept()  # wait for client
        handle_connection(connection)


if __name__ == "__main__":
    main()
