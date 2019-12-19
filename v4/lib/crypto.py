from time import sleep

import v4.event_loop as ev


def get_hash(obj, callback):

    def calculate_hash():
        print(f"Calculating hash for {obj}")
        sleep(1)
        return obj, "ThisIsYourHash"

    ev.register_blocking_task(calculate_hash, callback)