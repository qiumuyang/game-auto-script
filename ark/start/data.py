from enum import IntEnum
from utils.log import get_logger

from img.common import Box
from ..common import ark_intf

intf = ark_intf

logger = get_logger('Start', 'INFO')

GAME_ICON = 'start/icon.png'
START = 'start/start.png'
WAKEN = 'start/开始唤醒.png'
ACCOUNT_MANAGE = 'start/账号管理.png'
ACCOUNT_LOGIN = 'start/账号登录.png'
OK = 'ok.png'
NO = 'no.png'
LOGIN = 'start/登录.png'
ACCOUNT_INPUT = 'start/账号.png'
PASSWORD_INPUT = 'start/密码.png'
CONFIRM = 'start/确定.png'
AWARD_BOX = Box((587, 141), (691, 169))
GET_AWARD_BOX = Box((619, 619), (658, 657))

# TODO: add download-new-data check


class Status(IntEnum):
    Unknown = -1
    NotStarted = 0
    Start = 1
    Wake = 2
    WakeFailed = 3
    Login = 4
    DailyReward = 5
    Success = 6
    ExitConfirm = 7
    Update = 8


Status_pivot = {Status.NotStarted: GAME_ICON,
                Status.Start: [START, 'start/清除缓存.png'],
                Status.Wake: [WAKEN, ACCOUNT_MANAGE],
                Status.Login: ACCOUNT_LOGIN,
                Status.WakeFailed: 'start/请重新输入登录信息.png',
                Status.DailyReward: '获得物资-2.png',
                Status.Success: [
                    # sign in
                    'start/已签到.png',
                    # notice
                    '系统公告.png', '活动公告.png',
                    '系统公告-2.png', '活动公告-2.png',
                    # main scene
                    'main/好友.png',
                    # in battle
                    'battle/speed-1.png', 'battle/speed-2.png',
                    # post battle
                    'battle/行动结束.png', 'battle/剿灭结束.png',
                    # common
                    '返回.png', '快速访问.png', '返回-2.png', ],
                Status.ExitConfirm: '是否确认退出游戏.png',
                Status.Update: 'start/正在释放神经递质.png'
                }


def get_start_status() -> Status:
    scr = intf.screen()
    for status, pivot in Status_pivot.items():
        if isinstance(pivot, str):
            pivot = [pivot]
        if any(intf.img_match(img, scr) for img in pivot):
            if status == Status.Success:
                for img in pivot:
                    if intf.img_match(img, scr):
                        logger.debug('Success: ' + img)
                        break
            return status
    return Status.Unknown
