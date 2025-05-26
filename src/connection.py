from socket import socket

from config import ENCODING, SOCKET_BUFFER


class ConnectionManager:
    def __init__(self, conn: socket):
        self.buffer = ""
        self.conn = conn

    def __next_char(self) -> str:
        if len(self.buffer) == 0:
            chunk = self.conn.recv(SOCKET_BUFFER)
            if not chunk:
                raise ConnectionError("Connection closed before delimiter")
            self.buffer = chunk.decode(encoding=ENCODING)
        next, self.buffer = self.buffer[0], self.buffer[1:]
        return next

    def read_until(self, terminator: str, remove_terminator=True) -> str:
        data = ""
        while not data.endswith(terminator):
            data += self.__next_char()
        return data.removesuffix(terminator) if remove_terminator else data

    def read_n(self, n: int) -> str:
        data = ""
        for i in range(n):
            data += self.__next_char()
        return data

    def send(self, content: str):
        self.conn.sendall(bytes(content, encoding=ENCODING))

    def close(self):
        self.conn.close()
