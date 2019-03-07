import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from sqlalchemy.exc import SQLAlchemyError

from cats_controllers import cats, ping, post_cats
from cats_sqlalhemy import db_session
from settings import SERVER_PORT


class Server(BaseHTTPRequestHandler):
    urls = {"ping": ping, "cats": cats}

    def do_GET(self):
        data = parse_qs(urlparse(self.path).query)
        real_path = urlparse(self.path).path.strip("/")
        try:
            if real_path in self.urls:
                with db_session() as session:
                    self.server_response(*self.urls[real_path](data, session))
            else:
                self.server_response(
                    404,
                    {"status": "Nothing found", "exception": ""},
                    {"Content-type": "application/json"},
                )
        except SQLAlchemyError as err:
            self.server_response(
                500,
                {
                    "status": "No connection with database",
                    "exception": str(err.__cause__),
                },
                {"Content-type": "application/json"},
            )

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        body = self.rfile.read(content_length)
        try:
            with db_session() as session:
                self.server_response(*post_cats(body, session))
        except SQLAlchemyError as err:
            self.server_response(
                500,
                {
                    "status": "No connection with database",
                    "exception": str(err.__cause__),
                },
                {"Content-type": "text/html"},
            )

    def server_response(self, code: int, context: str, headers={}):
        self.send_response(code)
        for head in headers:
            self.send_header(head, headers[head])
        self.end_headers()

        if headers.get("Content-type", "text/html").endswith("json"):
            self.wfile.write(json.dumps(context).encode())
        else:
            self.wfile.write(str(context).encode())


def run(server_class=HTTPServer, handler_class=Server, port=SERVER_PORT):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)

    print("Starting httpd on port %d..." % port)
    httpd.serve_forever()


if __name__ == "__main__":
    run()
