from typing import Tuple
from .data import *
import configparser
import time
import os


def _load_user_account() -> Tuple[str, str]:
    cdir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(cdir, 'user.config')
    parser = configparser.ConfigParser()
    parser.read(path)
    return tuple(parser.get('user', key)
                 for key in ['account', 'password'])


def _login() -> None:
    intf.wait_img(LOGIN)
    account, password = _load_user_account()
    if intf.img_tap(ACCOUNT_INPUT, 1):
        # input account
        intf.text(account)
        intf.img_tap(CONFIRM)
        time.sleep(1)
    if intf.img_tap(PASSWORD_INPUT, 1):
        # input password
        intf.text(password)
        intf.img_tap(CONFIRM)
        time.sleep(1)
    intf.img_tap(LOGIN)


def start_game() -> None:
    logger.info('启动中')
    Next = {
        Status.NotStarted: GAME_ICON,
        Status.Start: START,
        Status.Wake: WAKEN,
        Status.WakeFailed: OK,
        Status.ExitConfirm: NO,
        Status.DailyReward: GET_AWARD_BOX,
    }
    prompt = True
    while 1:
        status = get_start_status()
        logger.debug(status)
        if status == Status.Unknown:
            pass
        elif status in Next:
            _next = Next[status]
            if isinstance(_next, str):  # image
                intf.img_tap(_next, 1)
            elif isinstance(_next, Box):  # box
                intf.tap(_next)
        elif status == Status.Login:
            intf.img_tap(ACCOUNT_LOGIN, 1)
            _login()
        elif status == Status.Success:
            break
        elif status == Status.Update:
            if prompt:
                logger.info('更新中')
                prompt = False

        time.sleep(2)
