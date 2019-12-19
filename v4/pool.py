import os
import queue
import threading
from dataclasses import dataclass
from typing import Callable, Type, Any


@dataclass
class Task:
    fn: Callable
    read_fd: Any
    write_fd: Any


class Pool:

    def __init__(self):
        self.threads = []
        self.queue = queue.Queue()
        self.return_val = {}
        self.lock = threading.Lock()

    def start(self):
        self.threads = [TaskProcessor(name='TaskProcessor', queue=self.queue, pool=self) for _ in range(4)]
        for t in self.threads:
            t.start()

    def submit(self, task: Task):
        self.queue.put(task)

    def set_return_val(self, fd, *val):
        self.lock.acquire(blocking=True)
        self.return_val[fd] = val
        self.lock.release()

    def get_return_val(self, fd):
        self.lock.acquire(blocking=True)
        val = self.return_val[fd]
        del self.return_val[fd]
        self.lock.release()
        return val


class TaskProcessor(threading.Thread):

    def __init__(self, group=None, target=None, name=None, pool: Pool = None, queue: queue.Queue = None, args=(), kwargs=None):
        super().__init__(group=group, target=target, name=name, args=args, kwargs=kwargs)
        self.queue: Type[queue.Queue] = queue
        self.pool: Pool = pool

    def run(self) -> None:
        while True:
            task = self.queue.get(block=True)
            self.process(task)

    def process(self, task: Task):
        val = task.fn()
        self.pool.set_return_val(task.read_fd, val)
        os.write(task.write_fd, str.encode("Done"))
        os.close(task.write_fd)
