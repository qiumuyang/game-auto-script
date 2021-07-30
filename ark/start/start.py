from typing import Tuple
from .data import *
from utils.log import get_logger
import configparser
import time
import os

logger = get_logger('Start')


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
    while 1:
        status = get_start_status()
        logger.debug(status)
        if status == Status.Unknown:
            pass
        elif status == Status.Not_start:
            intf.img_tap(GAME_ICON)
        elif status == Status.Start:
            intf.img_tap(START)
        elif status == Status.Wake:
            intf.img_tap(WAKEN)
        elif status == Status.Wake_fail:
            intf.img_tap(OK)
        elif status == Status.Login:
            intf.img_tap(ACCOUNT_LOGIN)
            _login()
        elif status == Status.Daily_award:
            intf.tap(GET_AWARD_BOX)
        elif status == Status.Success:
            break

        time.sleep(2)
