import enum
import select


class EventType(enum.Enum):
    Read = 1
    Write = 2


class EventLoop:

    def __init__(self):
        self.r_list = []
        self.w_list = []

        self.r_callbacks = {}
        self.w_callbacks = {}

    def register_for_read(self, fd, callback):
        self.r_list.append(fd)
        self.r_callbacks[fd] = callback

    def register_for_write(self, fd, callback):
        self.w_list.append(fd)
        self.w_callbacks[fd] = callback

    def start(self):
        while len(self.r_list) or len(self.w_list):
            r_list, w_list, _ = select.select(self.r_list, self.w_list, [])

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
start = _inst.start
