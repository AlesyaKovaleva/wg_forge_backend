from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from sqlalchemy.exc import SQLAlchemyError

from cats_controllers import Response, cats, ping, post_cats
from cats_sqlalhemy import db_session
from settings import SERVER_PORT

# from io import BytesIO


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
                    404, "Nothing found", {"Content-type": "text/html"}
                )
        except SQLAlchemyError:
            self.server_response(
                500, "No connection with database", {"Content-type": "text/html"}
            )

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        body = self.rfile.read(content_length)
        with db_session() as session:
            self.server_response(*post_cats(body, session))
        self.send_response(200)
        self.end_headers()
        # response = BytesIO()
        # response.write(b'This is POST request. ')
        # response.write(b'Received: ')
        # response.write(body)
        # self.wfile.write(response.getvalue())

    def server_response(self, code: int, context: str, headers: dict):
        self.send_response(code)
        if headers:
            for head in headers:
                self.send_header(head, headers[head])
        self.end_headers()
        self.wfile.write(context.encode())


def run(server_class=HTTPServer, handler_class=Server, port=SERVER_PORT):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)

    print("Starting httpd on port %d..." % port)
    httpd.serve_forever()


if __name__ == "__main__":
    run()
