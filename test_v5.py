from v5.scheduler import Scheduler
from v5.syscall import GetTid


def sanity_test():
    def ping():
        i = 0
        while i < 5:
            print(f"Ping {i}")
            i += 1
            yield

    def pong():
        i = 0
        while i < 5:
            print(f"Pong {i}")
            i += 1
            yield

    scheduler = Scheduler()
    scheduler.new_task(ping())
    scheduler.new_task(pong())
    scheduler.run()


def get_tid_test():
    def fn():
        tid = yield GetTid()
        print(f"My TID is {tid}")

    scheduler = Scheduler()
    scheduler.new_task(fn())
    scheduler.run()


if __name__ == '__main__':
    get_tid_test()
