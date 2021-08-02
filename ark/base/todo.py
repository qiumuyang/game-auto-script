from .data import *
import time


def collect_todo() -> None:
    assert(get_base_status() in [Status.Big, Status.Small])
    collected = False
    while 1:
        status = get_base_status()
        if status == Status.Todo_shown:
            for todo in TODO_LIST:
                intf.img_tap(todo, 1)
                time.sleep(1)
            collected = True
            intf.tap(TODO_BLANK)
        elif status in [Status.Small, Status.Big]:
            if collected:
                return
            if not intf.img_tap(TODO, 2):
                return
        time.sleep(2)
