from socket import socket

from config import ENCODING, SOCKET_BUFFER


class ConnectionManager:
    def __init__(self, conn: socket):
        self.buffer = bytearray()
        self.conn = conn

    def __next_byte(self) -> int:
        if len(self.buffer) == 0:
            chunk = self.conn.recv(SOCKET_BUFFER)
            if not chunk:
                raise ConnectionError("Connection closed before delimiter")
            self.buffer = bytearray(chunk)
        return self.buffer.pop(0)

    def read_until(self, terminator: bytes, remove_terminator=True) -> bytes:
        data = bytearray()
        while not data.endswith(terminator):
            data.append(self.__next_byte())
        return data.removesuffix(terminator) if remove_terminator else data

    def read_until_str(self, terminator: str, remove_terminator=True) -> str:
        return self.read_until(terminator.encode(ENCODING)).decode(ENCODING)

    def read_n(self, n: int) -> bytes:
        data = bytearray()
        for i in range(n):
            data.append(self.__next_byte())
        return data

    def send_str(self, content: str):
        self.send_bytes(bytes(content, encoding=ENCODING))

    def send_bytes(self, content: bytes):
        self.conn.sendall(content)

    def close(self):
        self.conn.close()
