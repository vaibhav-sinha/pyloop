import select
import socket


class Server:

    def __init__(self):
        self.listener = None
        self.readfds = []
        self.writefds = []

        self.req_dict = {}

    def setup(self, port):
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setblocking(False)
        self.listener.bind(('0.0.0.0', port))
        self.listener.listen(100)
        self.readfds.append(self.listener)

    def run(self):
        while True:
            rlist, wlist, _ = select.select(self.readfds, self.writefds, [])

            for rsocket in rlist:
                if rsocket is self.listener:
                    client, _ = rsocket.accept()
                    self.readfds.append(client)
                elif rsocket in self.req_dict.keys():
                    req = self.req_dict[rsocket]
                    data = rsocket.recv(1000)
                    self.readfds.remove(rsocket)
                    self.writefds.append(req["req_socket"])
                    del self.req_dict[rsocket]
                else:
                    chunk = rsocket.recv(1000)
                    parts = chunk.decode("utf-8").split('\r\n')
                    parts = parts[0].split(' ')
                    path = parts[1]

                    k = self.do_io(rsocket)
                    self.readfds.remove(rsocket)

            for wsocket in wlist:
                if wsocket in self.req_dict.keys():
                    wsocket.sendall(str.encode("GET / HTTP/1.1\r\nHost: www.google.com\r\n\r\n"))
                    self.readfds.append(wsocket)
                    self.writefds.remove(wsocket)
                else:
                    response = f'''HTTP/1.1 200 OK
                    Date: Mon, 27 Jul 2009 12:28:53 GMT
                    Server: Apache/2.2.14 (Win32)
                    Last-Modified: Wed, 22 Jul 2009 19:15:56 GMT
                    Content-Type: text/html
                    Server: pyloop
                    Connection: Closed

                    <html>
                    <body>
                    <h1>Hello, World!</h1>
                    </body>
                    </html>'''

                    wsocket.send(str.encode(response))
                    wsocket.close()
                    self.writefds.remove(wsocket)

    def do_nothing(self):
        return 0

    def do_compute(self):
        k = 0
        for i in range(100000):
            k = i * i
        return k

    def do_io(self, req_socket):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("172.217.26.174", 80))

        self.req_dict[s] = {"req_socket": req_socket}
        self.writefds.append(s)
        return 0


if __name__ == '__main__':
    server = Server()
    server.setup(9876)
    server.run()
