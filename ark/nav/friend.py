from .navigate import move_to_main_scene
from .data import *
from img.reco import recognize
import time

VISIT_NEXT_1 = 'friend/访问下位-有.png'
VISIT_NEXT_2 = 'friend/访问下位-无.png'
VISIT_NEXT_BOX = Box.from_size((1091, 578), (189, 101))

FRIEND_PIVOT = ['friend/我的信息.png', 'friend/我的信息-2.png']
FRIEND_LIST = 'friend/好友列表.png'
VISIT_BASE = 'friend/访问基建.png'
FRIEND_NAME_RECO_BOX = Box.from_size((421, 17), (216, 40))
BACK = '返回.png'
BACK_OK = 'ok-2.png'
BACK_PIVOT = 'friend/是否确定返回好友列表.png'
UP_LIMIT = 'friend/上限.png'


def _do_next_visit() -> bool:
    while 1:
        visit_img = intf.screen(box=VISIT_NEXT_BOX)
        if intf.img_cmp(visit_img, VISIT_NEXT_1):
            return True
        if intf.img_cmp(visit_img, VISIT_NEXT_2):
            return False
        time.sleep(1.5)
    return False


def _get_friend_name() -> str:
    scr = intf.screen(box=FRIEND_NAME_RECO_BOX)
    return recognize(scr).replace('的会客室', '')


def collect_friend_credit():
    move_to_main_scene()
    while not intf.wait_img(FRIEND_PIVOT, 0):
        intf.img_tap(FRIEND, 0)
    while not intf.img_match(VISIT_BASE):
        intf.img_tap(FRIEND_LIST, 0)
    intf.img_tap(VISIT_BASE, 3)

    prev_name = ''
    while _do_next_visit():
        name = _get_friend_name()
        if intf.img_match(UP_LIMIT):
            logger.info('今日参与交流已达上限')
            break
        if prev_name != name:
            logger.info(f'当前好友 {name}，访问下一位好友')
            intf.img_tap(VISIT_NEXT_1)
        time.sleep(1)

    logger.info('返回好友列表')
    while 1:
        intf.img_tap(BACK, 1)
        if intf.img_match(BACK_PIVOT):
            break

    intf.img_tap(BACK_OK, 3)
