from dataclasses import asdict, dataclass, field
from http import HTTPMethod, HTTPStatus
import logging
import mimetypes

from config import ENCODING, HTTP_VERSION
from src import utils
from src.connection import ConnectionManager

log = logging.getLogger()

HTTP_NEWLINE = "\r\n"

TEXT_MIMETYPES = [
    "text/",
    "application/json",
    "application/javascript",
    "application/xml",
    "application/ld+json",
    "application/yaml",
]


@dataclass
class HTTPRequest:
    method: HTTPMethod
    path: str
    http_version: str
    headers: dict[str, str]
    body: bytes | None


@dataclass
class HTTPResponse:
    status: HTTPStatus
    http_version: str | None = None
    headers: dict[str, str] | None = None
    body: bytes | None = None
    mimetype: str | None = None


def is_text(mimetype: str) -> bool:
    return any(mimetype.startswith(mime) for mime in TEXT_MIMETYPES)


class HTTPClient:
    def __init__(self, conn: ConnectionManager):
        self.conn = conn

    def read_request(self) -> HTTPRequest:
        method = HTTPMethod(self.conn.read_until_str(" ").upper())
        path = self.conn.read_until_str(" ")
        http_version = self.conn.read_until_str(HTTP_NEWLINE)
        headers = {}
        while True:
            header = self.conn.read_until_str(HTTP_NEWLINE)
            if len(header) == 0:
                break
            else:
                [key, val] = header.split(": ", 1)
                headers[key.lower()] = val
        content_length = headers.get("content-length")
        body = None
        if content_length is not None:
            body = self.conn.read_n(int(content_length))

        req = HTTPRequest(
            method=method,
            path=path,
            http_version=http_version,
            headers=headers,
            body=body,
        )
        log.info(f"Request: {utils.object_str(asdict(req))}")
        return req

    def send_res(self, res: HTTPResponse):
        res.http_version = utils.get_or(res.http_version, HTTP_VERSION)
        res.headers = utils.get_or(res.headers, {})
        res.mimetype = utils.get_or(res.mimetype, "text/plain")

        log.info(f"Response: {utils.object_str(asdict(res))}")
        data = f"{res.http_version.upper()} {res.status.value} {res.status.phrase}{HTTP_NEWLINE}"
        if res.body is not None:
            res.headers["Content-Type"] = (
                f"{res.mimetype}{f"; charset={ENCODING}" if is_text(res.mimetype) else ""}"
            )
            res.headers["Content-Length"] = len(res.body)
        for key, val in res.headers.items():
            data += f"{key}: {val}{HTTP_NEWLINE}"
        data += f"{HTTP_NEWLINE}"
        self.conn.send_str(data)
        if res.body is not None:
            self.conn.send_bytes(res.body)

    def close(self):
        self.conn.close()
