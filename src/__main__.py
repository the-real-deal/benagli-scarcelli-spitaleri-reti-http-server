import logging
import mimetypes
import signal
import sys
from http import HTTPMethod, HTTPStatus
from os import path
from pathlib import Path
from config import HOST, HTTP_VERSION, N_CONNECTIONS, PORT, WEB_ROOT
from src import utils
from src.connection import ConnectionManager
from src.server import HTTPClient, HTTPResponse
import socket

logging.basicConfig(
    format="[%(levelname)s@%(asctime)s] %(message)s",
    level=logging.NOTSET,
)
log = logging.getLogger()

ALLOWED_METHODS = [
    HTTPMethod.GET,
]

HTML_INDEX_PAGE = "index.html"


def resolve_page_path(req_path: str) -> Path:
    page_path = Path(WEB_ROOT, path.normpath(req_path.removeprefix("/")))

    if page_path.is_dir():
        return page_path.joinpath(HTML_INDEX_PAGE)

    if not page_path.exists() and len(page_path.suffix) == 0:
        candidate = page_path.with_suffix(".html")
        if candidate.name != HTML_INDEX_PAGE:
            return candidate

    return page_path


def send_page(req_path: str, http_client: HTTPClient, status=HTTPStatus.OK):
    page_path = resolve_page_path(req_path)

    log.info(f"Requested page: {page_path}")
    if not page_path.exists():
        raise FileNotFoundError()

    mymetype, _ = mimetypes.guess_type(page_path)
    with open(page_path, "r") as page:
        http_client.send_res(
            HTTPResponse(
                status=status,
                body=page.read(),
                mymetype=mymetype,
            )
        )


def main():
    server_address = (HOST, PORT)
    server_socket = socket.socket(
        family=socket.AF_INET,
        type=socket.SOCK_STREAM,
    )

    # allow immediate reuse of the port
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def shutdown(_signum=None, _frame=None):
        log.info("Shutting down server...")
        try:
            server_socket.close()
        except Exception as e:
            log.error(f"Error closing server socket: {e}")
        sys.exit(0)

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, shutdown)  # Handle Ctrl+C
    signal.signal(signal.SIGTERM, shutdown)  # Handle termination (e.g., kill)

    try:
        server_socket.bind(server_address)
        server_socket.listen(N_CONNECTIONS)
        log.info(f"Socket listening on {utils.address_string(server_address)}")

        while True:
            conn, addr = server_socket.accept()
            log.info(f"Accepted connection from {utils.address_string(addr)}")
            http_client = HTTPClient(ConnectionManager(conn))
            try:
                req = http_client.read_request()
                if req.http_version.upper() != HTTP_VERSION.upper():
                    http_client.send_res(
                        HTTPResponse(
                            status=HTTPStatus.HTTP_VERSION_NOT_SUPPORTED,
                        )
                    )
                elif req.method not in ALLOWED_METHODS:
                    http_client.send_res(
                        HTTPResponse(
                            status=HTTPStatus.METHOD_NOT_ALLOWED,
                        )
                    )
                else:
                    send_page(req.path, http_client)
            except FileNotFoundError:
                http_client.send_res(
                    HTTPResponse(status=HTTPStatus.NOT_FOUND, body="Not found")
                )
            except Exception as e:
                http_client.send_res(
                    HTTPResponse(
                        status=HTTPStatus.INTERNAL_SERVER_ERROR,
                        body=str(e),
                    )
                )
            finally:
                http_client.close()
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
