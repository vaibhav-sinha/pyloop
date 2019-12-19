import v3.event_loop as ev


def set_timeout(seconds, callback):
    ev.register_timer(seconds, callback)

