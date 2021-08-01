from adb.adb import Key
from .data import *
import time


def move_to_main_scene():
    # temp
    logger.info('移动至主界面')
    while 1:
        scene = get_current_scene()
        if scene == Scene.Main:
            return
        elif scene == Scene.ExitConfirm:
            intf.img_tap(NO, 1)
        elif scene == Scene.BattleIn:
            # wait until battle finish
            continue
        elif scene == Scene.GetResource:
            intf.tap(COLLECT_REWARD_BOX)
        else:
            intf.keyevent(Key.BACK)
        time.sleep(1)


def move_to_last_level() -> bool:
    # temp
    move_to_main_scene()
    while 1:
        scene = get_current_scene()
        if scene == Scene.Main:
            intf.img_tap(TERMINAL, 1)
        elif scene == Scene.Terminal:
            if not intf.img_tap(LAST_BATTLE, 2):
                logger.critical('[前往上一次作战] 不存在')
                return False
        elif scene == Scene.BattlePre:
            return True
        time.sleep(1)


def move_to_shop():
    # temp
    move_to_main_scene()
    while 1:
        scene = get_current_scene()
        if scene == Scene.Main:
            intf.img_tap(PURCHASE_CENTER, 2)
        elif scene == Scene.Shop:
            return
        else:
            move_to_main_scene()
        time.sleep(1)
