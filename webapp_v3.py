from v3.lib.http_server import *
from v3.lib.http_client import *
from v3.lib.timer import *
import v3.event_loop as ev


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


def sleep(request, send_response):
    def on_wakeup():
        response = HttpResponse(HttpStatus.OK, {}, "<html><body>I woke up</body></html>")
        send_response(response)
    set_timeout(5, on_wakeup)


server.register_handler("/hi", hi)
server.register_handler("/connect", connect)
server.register_handler("/sleep", sleep)
server.run()

ev.start()
