from v5.lib.http_server import *
from v5.lib.http_client import *
from v5.scheduler import *


server = HttpServer()
server.setup(9898)


def hi(request):
    return HttpResponse(HttpStatus.OK, {}, "<html><body>Hello World</body></html>")


def connect(request):
    data = yield get("http://www.google.com?q=india")
    return HttpResponse(HttpStatus.OK, {}, data)


server.register_handler("/hi", hi)
server.register_handler("/connect", connect)
new_task(server.run())

run()

