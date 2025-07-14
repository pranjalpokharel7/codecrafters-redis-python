import socket  # noqa: F401
import threading

from app.types.types import Array

MAX_BUF_SIZE = 512

from app.types import resp_type_from_bytes


def handle_connection(client_socket: socket.socket):
    while True:
        chunk = client_socket.recv(MAX_BUF_SIZE)
        if not chunk:  # empty buffer means client has disconnected
            break

        parsed_input, _ = resp_type_from_bytes(chunk)

        # parsing further to commands will be refactored in the next stage
        response = b"+PONG\r\n"
        if isinstance(parsed_input, Array):
            array = parsed_input.value
            command = array[0]
            args = array[1:]
            if command.value == "ECHO":
                response = bytes(args[0])

        client_socket.sendall(response)


def main():
    print("Logs from your program will appear here!")
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)

    while True:
        client_socket, _ = server_socket.accept()  # wait for client
        threading.Thread(target=handle_connection, args=(client_socket,)).start()


if __name__ == "__main__":
    main()
