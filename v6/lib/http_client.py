import socket
from urllib.parse import urlparse
from v6.syscall import WaitForRead, WaitForWrite


class HttpClient:

    @staticmethod
    def get(url):
        parse_result = urlparse(url)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setblocking(False)
        s.connect_ex(("172.217.26.174", parse_result.port if parse_result.port else 80))
        yield WaitForWrite(s)

        path = parse_result.path if parse_result.path else "/"
        query = "?" + parse_result.query if parse_result.query else ""
        request = f"GET {path}{query} HTTP/1.1\r\nHost: {parse_result.hostname}\r\n\r\n"
        s.sendall(str.encode(request))
        yield WaitForRead(s)

        data = s.recv(1000)
        s.close()
        return data


get = HttpClient.get
