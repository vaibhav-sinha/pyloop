from v2.lib.http_server import *
from v2.lib.http_client import *
import v2.event_loop as ev


server = HttpServer()
server.setup(9898)


def hi(request, send_response):
    response = HttpResponse(HttpStatus.OK, {}, "<html><body>Hello World</body></html>")
    send_response(response)


def connect(request, send_response):
    def on_get_response(data):
        response = HttpResponse(HttpStatus.OK, {}, data)
        send_response(response)

    get("http://www.google.com?q=india", on_get_response)


server.register_handler("/hi", hi)
server.register_handler("/connect", connect)
server.run()

ev.start()
