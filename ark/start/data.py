from enum import IntEnum

from img.common import Box
from ..common import ark_intf

intf = ark_intf

GAME_ICON = 'start/icon.png'
START = 'start/start.png'
WAKEN = 'start/开始唤醒.png'
ACCOUNT_MANAGE = 'start/账号管理.png'
ACCOUNT_LOGIN = 'start/账号登录.png'
OK = 'ok.png'
LOGIN = 'start/登录.png'
ACCOUNT_INPUT = 'start/账号.png'
PASSWORD_INPUT = 'start/密码.png'
CONFIRM = 'start/确定.png'
AWARD_BOX = Box((587, 141), (691, 169))
GET_AWARD_BOX = Box((619, 619), (658, 657))

# TODO: add download-new-data check


class Status(IntEnum):
    Unknown = -1
    Not_start = 0
    Start = 1
    Wake = 2
    Wake_fail = 3
    Login = 4
    Daily_award = 5
    Success = 6


Status_pivot = {Status.Not_start: GAME_ICON,
                Status.Start: [START, 'start/清除缓存.png'],
                Status.Wake: [WAKEN, ACCOUNT_MANAGE],
                Status.Login: ACCOUNT_LOGIN,
                Status.Wake_fail: 'start/请重新输入登录信息.png',
                Status.Daily_award: '获得物资-2.png',
                Status.Success: ['系统公告.png', '活动公告.png',
                                 'main/公告.png', 'main/好友.png',
                                 'battle/开始行动-1.png',
                                 '返回.png', '快速访问.png']
                }


def get_start_status() -> Status:
    scr = intf.screen()
    for status, pivot in Status_pivot.items():
        if isinstance(pivot, str):
            pivot = [pivot]
        if any(intf.img_match(img, scr) for img in pivot):
            return status
    return Status.Unknown
