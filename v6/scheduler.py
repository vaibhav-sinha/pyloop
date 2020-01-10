import queue
import select
from types import GeneratorType


class Task:

    next_task_id = 0

    def __init__(self, fn):
        self.target = fn
        self.send_val = None
        self.task_id = Task.get_next_task_id()
        self.stack = []

    def run(self):
        from v6.syscall import Syscall

        while True:
            try:
                result = self.target.send(self.send_val)
                if isinstance(result, Syscall):
                    return result

                if isinstance(result, GeneratorType):
                    self.stack.append(self.target)
                    self.send_val = None
                    self.target = result
                else:
                    if not self.stack:
                        return
                    self.send_val = result
                    self.target = self.stack.pop()
            except StopIteration as e:
                if not self.stack:
                    raise
                self.send_val = e.value
                self.target = self.stack.pop()

    @staticmethod
    def get_next_task_id():
        task_id = Task.next_task_id
        Task.next_task_id += 1
        return task_id


class Scheduler:

    def __init__(self):
        self.ready_queue = queue.Queue()
        self.wait_r_tasks = {}
        self.wait_w_tasks = {}
        self.tasks = {}

    def new_task(self, fn):
        task = Task(fn)
        self.tasks[task.task_id] = task
        self.schedule_to_run(task)

    def schedule_to_run(self, task):
        self.ready_queue.put(task)

    def remove_task(self, task):
        del self.tasks[task.task_id]

    def wait_for_read(self, task, fd):
        self.wait_r_tasks[fd] = task

    def wait_for_write(self, task, fd):
        self.wait_w_tasks[fd] = task

    def io_poll(self):
        while True:
            if not self.ready_queue.empty():
                timeout = 0
            else:
                timeout = None

            r_list, w_list, _ = select.select(self.wait_r_tasks, self.wait_w_tasks, [], timeout)

            for fd in r_list:
                task = self.wait_r_tasks.pop(fd)
                self.schedule_to_run(task)

            for fd in w_list:
                task = self.wait_w_tasks.pop(fd)
                self.schedule_to_run(task)

            yield

    def run(self):
        from v6.syscall import Syscall

        self.new_task(self.io_poll())

        while self.tasks:
            task = self.ready_queue.get()
            try:
                result = task.run()
                if result is None:
                    self.schedule_to_run(task)
                elif isinstance(result, Syscall):
                    result.execute(self, task)
            except StopIteration:
                self.remove_task(task)


_inst = Scheduler()
run = _inst.run
new_task = _inst.new_task
