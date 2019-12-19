import select
import socket


class Server:

    def __init__(self):
        self.listener = None
        self.readfds = []
        self.writefds = []

        self.connect_dict = {}
        self.read_dict = {}

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
                    self.writefds.append(client)
                else:
                    if rsocket in wlist:
                        chunk = rsocket.recv(1000)
                        parts = chunk.decode("utf-8").split('\r\n')
                        parts = parts[0].split(' ')
                        path = parts[1]

                        k = self.do_compute()

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
<h2>{path}</h2>
<h3>{k}</h3>
</body>
</html>'''

                        rsocket.send(str.encode(response))
                        rsocket.close()

                        self.readfds.remove(rsocket)
                        self.writefds.remove(rsocket)

    def do_nothing(self):
        return 0

    def do_compute(self):
        k = 0
        for i in range(100000):
            k = i * i
        return k


if __name__ == '__main__':
    server = Server()
    server.setup(9876)
    server.run()
