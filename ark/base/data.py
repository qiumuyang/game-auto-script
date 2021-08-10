from enum import IntEnum
import time
from img.common import Box
from utils.log import get_logger
from ..common import ark_intf

intf = ark_intf

logger = get_logger('Base')

BACK = '返回.png'

LEAVE = 'base/是否确认离开罗德岛基建.png'
VIEW_SHIFT = 'base/进驻总览.png'
TODO = 'base/待办.png'
TODO_LIST = [f'base/{event}.png' for event in ['可收获', '订单交付', '干员信赖']]
TODO_BLANK = Box((1020, 534), (1260, 654))
DRONE_RECO_BOX = Box.from_size((767, 22), (48, 26))

ROOM_TITLE_BOX = Box.from_size((427, 20), (160, 32))
ROOM_NAMES = ['控制中枢', '会客室', '加工站', '办公室', '训练室',
              '贸易站', '发电站', '制造站', '宿舍', ]
ROOM_PIVOT = 'base/room-pivot.png'
ROOM_X_OFFSET = -760
ROOM_Y_OFFSET = -6
ROOM_SIZE = (796, 134)
ROOM_NAME_BOXES = [Box.from_size((5, 11), (w, 27))
                   for w in [104, 79, 54]]
OPERATOR_RECO_BOX = [Box.from_size((191 + i * 112, 0), (112, ROOM_SIZE[1]))
                     for i in range(5)]
OPERATOR_TAP_BOX = [Box.from_size((201 + i * 112, 17), (92, 92))
                    for i in range(5)]
OPERATOR_EMPTY = 'base/empty.png'
OPERATOR_INVALID = 'base/invalid.png'
OPERATOR_MOOD_BOX = Box.from_size((29, 114), (77, 4))
MAX_MOOD = 24


class Status(IntEnum):
    Unknown = -1
    MainBig = 0
    MainSmall = 1
    TodoShown = 2
    Shift = 3
    Room = 4
    Manu = 5


Status_Pivot = {
    Status.TodoShown: 'base/待办事项.png',
    Status.MainBig: ['base/控制中枢-1.png', 'base/贸易站-1.png',
                     'base/制造站-1.png', 'base/发电站-1.png', ],
    Status.MainSmall: ['base/控制中枢-2.png', 'base/贸易站-2.png',
                       'base/制造站-2.png', 'base/发电站-2.png', ],
    Status.Shift: 'base/进驻总览-2.png',
    Status.Room: ['base/进驻信息.png', 'base/设施信息.png'],
    Status.Manu: ['base/生产份数.png']
}


def get_base_status() -> Status:
    scr = intf.screen()
    for status, pivot in Status_Pivot.items():
        if isinstance(pivot, str):
            pivot = [pivot]
        if any(intf.img_match(img, scr) for img in pivot):
            return status
    return Status.Unknown


def move_to_main_base():
    # only can be used when in base
    # use 'nav.navigate.move_to_base' to move into base
    logger.info('移动至基建主界面')
    while 1:
        status = get_base_status()
        if status in [Status.MainBig, Status.MainSmall]:
            break
        else:
            intf.img_tap(BACK, 0.5)
        time.sleep(1.5)
