import socket  # noqa: F401
import threading

MAX_BUF_SIZE = 512


def handle_connection(client_socket: socket.socket):
    buf = b""
    while True:
        chunk = client_socket.recv(MAX_BUF_SIZE)
        if not chunk:  # empty buffer means client has disconnected
            break

        buf += chunk # handle this in the parsing step 

        client_socket.sendall(b"+PONG\r\n")


def main():
    print("Logs from your program will appear here!")
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)

    while True:
        client_socket, _ = server_socket.accept()  # wait for client
        threading.Thread(target=handle_connection, args=(client_socket,)).start()


if __name__ == "__main__":
    main()
