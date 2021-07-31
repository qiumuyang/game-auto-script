from .data import *
from .navigate import move_to_main_scene
import time


def _collect_request(pivot: str, goto: str) -> None:
    while 1:
        scene = get_current_scene()
        if scene == Scene.Request:
            break
        elif scene == Scene.Main:
            intf.img_tap(REQUEST, 1)
        else:
            move_to_main_scene()
        time.sleep(1)

    # while not intf.img_match(pivot):
    #     intf.img_tap(goto, 1)
    #     time.sleep(1)
    intf.img_tap(goto, 1)
    intf.img_tap(pivot, 1)

    # collect
    if intf.img_tap(COLLECT_ALL, 2):
        # get reward
        if intf.wait_img('获得物资-2.png', 2):
            logger.info('收取任务奖励')
            intf.tap(COLLECT_REWARD_BOX)


def collect_request_reward():
    for pivot, goto in [('request/日常任务-1.png', 'request/日常任务-2.png'),
                        ('request/周常任务-1.png', 'request/周常任务-2.png'), ]:
        _collect_request(pivot, goto)
        time.sleep(1)
