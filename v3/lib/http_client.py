import socket
from dataclasses import dataclass
from typing import Callable
from urllib.parse import urlparse, ParseResult
import v3.event_loop as ev


@dataclass
class ActiveRequest:
    parse_result: ParseResult
    callback: Callable


class HttpClient:

    def __init__(self):
        self.active_requests = {}

    def get(self, url, callback):
        parse_result = urlparse(url)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setblocking(False)
        s.connect_ex(("172.217.26.174", parse_result.port if parse_result.port else 80))
        self.active_requests[s] = ActiveRequest(parse_result, callback)
        ev.register_for_write(s, self._on_ready_for_write)

    def _on_ready_for_write(self, event_type, fd):
        active_request = self.active_requests[fd]
        path = active_request.parse_result.path if active_request.parse_result.path else "/"
        query = "?" + active_request.parse_result.query if active_request.parse_result.query else ""
        request = f"GET {path}{query} HTTP/1.1\r\nHost: {active_request.parse_result.hostname}\r\n\r\n"
        fd.sendall(str.encode(request))
        ev.register_for_read(fd, self._on_ready_for_read)

    def _on_ready_for_read(self, event_type, fd):
        active_request = self.active_requests[fd]
        data = fd.recv(1000)
        fd.close()
        del self.active_requests[fd]
        active_request.callback(data)


_inst = HttpClient()

get = _inst.get
