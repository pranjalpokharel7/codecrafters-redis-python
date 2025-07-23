import socket


class StreamingSocketReader:
    def __init__(self, sock: socket.socket, buf_size: int = 512):
        self.sock = sock
        self.uid = f"{sock.getpeername()[0]}:{sock.getpeername()[1]}"
        self.buffer = b""
        self.buf_size = buf_size

    def read_next_chunk(self):
        chunk = self.sock.recv(self.buf_size)
        if not chunk:
            raise ConnectionResetError("Socket closed by peer")
        self.buffer += chunk

    def read_and_update_buffer(self, callback):
        """
        Read element from buffer and update after read.
        """
        while True:
            try:
                element, consumed = callback(self.buffer)
                self.buffer = self.buffer[consumed:]
                return element
            except Exception:
                self.read_next_chunk()
