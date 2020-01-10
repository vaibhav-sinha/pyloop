import socket

from v6.syscall import WaitForRead, WaitForWrite, NewTask


class HttpStatus:
    OK = "200 OK"
    BAD_REQUEST = "400 Bad Request"
    NOT_FOUND = "404 Not Found"


class HttpRequest:

    def __init__(self, path):
        self.path = path


class HttpResponse:

    def __init__(self, status=None, headers=None, body=None):
        self.headers = headers if headers else {}
        self.body = body
        self.status = status

    def add_header(self, name, value):
        self.headers[name] = value

    def set_status(self, status):
        self.status = status

    def set_body(self, body):
        self.body = body


class HttpServer:

    def __init__(self):
        self.listener = None
        self.routes = {}
        self.responses = {}

    def setup(self, port):
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setblocking(False)
        self.listener.bind(('0.0.0.0', port))
        self.listener.listen(100)

    def register_handler(self, path, handler):
        self.routes[path] = handler

    def run(self):
        while True:
            yield WaitForRead(self.listener)
            client, _ = self.listener.accept()
            yield NewTask(self.handle_client(client))

    def handle_client(self, client):
        yield WaitForRead(client)

        chunk = client.recv(1000)
        parts = chunk.decode("utf-8").split('\r\n')
        parts = parts[0].split(' ')
        path = parts[1] if parts else ''

        handler = self.routes.get(path, None)
        if not handler:
            handler = self._404_handler

        response = yield handler(HttpRequest(path))
        yield WaitForWrite(client)

        http_std_response = f'''HTTP/1.1 {response.status}
                        Date: Mon, 27 Jul 2009 12:28:53 GMT
                        Server: PyLoop
                        Last-Modified: Wed, 22 Jul 2009 19:15:56 GMT
                        Content-Type: text/html
                        Connection: Closed

                        {response.body}'''

        client.send(str.encode(http_std_response))
        client.close()

    @staticmethod
    def _404_handler(request):
        yield HttpResponse(HttpStatus.NOT_FOUND, {}, f"<html><body>Could not find URL {request.path}</body></html>")
