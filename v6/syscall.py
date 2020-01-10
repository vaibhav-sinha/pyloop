import abc

from v6.scheduler import Scheduler, Task


class Syscall(abc.ABC):

    @abc.abstractmethod
    def execute(self, scheduler: Scheduler, task: Task):
        pass


class GetTid(Syscall):

    def execute(self, scheduler: Scheduler, task: Task):
        task.send_val = task.task_id
        scheduler.schedule_to_run(task)


class WaitForRead(Syscall):

    def __init__(self, fd):
        self.fd = fd

    def execute(self, scheduler: Scheduler, task: Task):
        scheduler.wait_for_read(task, self.fd)


class WaitForWrite(Syscall):

    def __init__(self, fd):
        self.fd = fd

    def execute(self, scheduler: Scheduler, task: Task):
        scheduler.wait_for_write(task, self.fd)


class NewTask(Syscall):

    def __init__(self, fn):
        self.fn = fn

    def execute(self, scheduler: Scheduler, task: Task):
        scheduler.new_task(fn=self.fn)
        scheduler.schedule_to_run(task)

