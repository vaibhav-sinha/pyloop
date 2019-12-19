import threading
import requests
import datetime


class MultiThreadedClient:

    def __init__(self):
        self.threads = []

    def run(self, concurrency, loops):
        start_time = datetime.datetime.now()
        for i in range(concurrency):
            t = HttpClientThread(id=i, loops=loops)
            self.threads.append(t)

        for t in self.threads:
            t.start()

        for t in self.threads:
            t.join()

        print(f"Time taken = {datetime.datetime.now() - start_time}")


class HttpClientThread(threading.Thread):

    def __init__(self, group=None, target=None, name=None, id: int = None, loops=None, args=(), kwargs=None):
        super().__init__(group=group, target=target, name=name, args=args, kwargs=kwargs)
        self.id = id
        self.loops = loops

    def run(self) -> None:
        for i in range(self.loops):
            response = requests.get(f'http://localhost:9898/connect')
            print(f"Response code = {response.status_code} for request {self.id}_{i}")


if __name__ == '__main__':
    client = MultiThreadedClient()
    client.run(10, 100)

    # 50s   vs 43s   - 100 * 100 requests - Do nothing
    # 1m20s vs 1m21s - 100 * 100 requests - Do compute
    # 9m20s vs 59s   - 10  * 100 requests - Do IO
