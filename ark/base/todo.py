from .data import *
import time


def collect_todo() -> None:
    logger.info('基建待办事项')
    move_to_main_base()
    assert(get_base_status() in [Status.MainBig, Status.MainSmall])

    collected = False
    while 1:
        status = get_base_status()
        if status == Status.TodoShown:
            for todo in TODO_LIST:
                intf.img_tap(todo, 1)
                time.sleep(1)
            collected = True
            intf.tap(TODO_BLANK)
        elif status in [Status.MainSmall, Status.MainBig]:
            if collected:
                return
            if not intf.img_tap(TODO, 2):
                logger.info('没有未处理的事项')
                return
        else:
            intf.img_tap(BACK, 1)
        time.sleep(2)
