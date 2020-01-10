from v6.lib.http_server import *
from v6.lib.http_client import *
from v6.scheduler import *


server = HttpServer()
server.setup(9898)


def hi(request):
    yield HttpResponse(HttpStatus.OK, {}, "<html><body>Hello World</body></html>")


def connect(request):
    data = yield get("http://www.google.com?q=india")
    yield HttpResponse(HttpStatus.OK, {}, data)


server.register_handler("/hi", hi)
server.register_handler("/connect", connect)
new_task(server.run())

run()

