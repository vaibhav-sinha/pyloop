import enum
import os
import select
from datetime import datetime, timedelta
from heapq import heappush, heappop

from v4.pool import Pool, Task


class EventType(enum.Enum):
    Read = 1
    Write = 2
    Timer = 3


class EventLoop:

    def __init__(self):
        self.r_list = []
        self.w_list = []

        self.r_callbacks = {}
        self.w_callbacks = {}

        self.timers = []
        self.default_wait_timeout = 0.1

        self.pool = Pool()

    def register_for_read(self, fd, callback):
        self.r_list.append(fd)
        self.r_callbacks[fd] = callback

    def register_for_write(self, fd, callback):
        self.w_list.append(fd)
        self.w_callbacks[fd] = callback

    def register_timer(self, seconds, callback):
        invocation_time = datetime.now() + timedelta(seconds=seconds)
        heappush(self.timers, (invocation_time, callback))

    def register_blocking_task(self, fn, callback):
        read_fd, write_fd = os.pipe()

        self.register_for_read(read_fd, self._get_blocking_task_callback(callback))

        task = Task(fn, read_fd, write_fd)
        self.pool.submit(task)

    def _get_blocking_task_callback(self, callback):
        def _blocking_task_callback(_, fd):
            val = self.pool.get_return_val(fd)
            os.close(fd)
            callback(*val[0])

        return _blocking_task_callback

    def start(self):
        self.pool.start()

        while len(self.r_list) or len(self.w_list) or len(self.timers):
            timeout = self.default_wait_timeout
            if len(self.timers) > 0:
                now = datetime.now()
                if self.timers[0][0] > now:
                    timeout = (self.timers[0][0] - now).total_seconds()
                else:
                    timeout = 0

            r_list, w_list, _ = select.select(self.r_list, self.w_list, [], timeout)

            now = datetime.now()

            for t in self.timers:
                if t[0] < now:
                    heappop(self.timers)
                    callback = t[1]
                    callback()
                else:
                    break

            for r in r_list:
                self.r_list.remove(r)
                callback = self.r_callbacks.pop(r)
                callback(EventType.Read, r)

            for w in w_list:
                self.w_list.remove(w)
                callback = self.w_callbacks.pop(w)
                callback(EventType.Write, w)


_inst = EventLoop()

register_for_read = _inst.register_for_read
register_for_write = _inst.register_for_write
register_timer = _inst.register_timer
register_blocking_task = _inst.register_blocking_task
start = _inst.start
