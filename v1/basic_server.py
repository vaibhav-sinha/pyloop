import socket


class Server:

    def __init__(self):
        self.listener = None

    def setup(self, port):
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.bind(('0.0.0.0', port))
        self.listener.listen(100)

    def run(self):
        while True:
            rsocket, _ = self.listener.accept()
            chunk = rsocket.recv(1000)
            parts = chunk.decode("utf-8").split('\r\n')
            parts = parts[0].split(' ')
            path = parts[1] if parts else ''

            k = self.do_io()

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
            <h2>{k}</h2>
            </body>
            </html>'''

            rsocket.send(str.encode(response))
            rsocket.close()

    def do_nothing(self):
        return 0

    def do_compute(self):
        k = 0
        for i in range(100000):
            k = i * i
        return k

    def do_io(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s.connect(("172.217.26.174", 80))
        s.sendall(str.encode("GET / HTTP/1.1\r\nHost: www.google.com\r\n\r\n"))
        data = s.recv(1000)
        s.close()
        return 0


if __name__ == '__main__':
    server = Server()
    server.setup(9875)
    server.run()
