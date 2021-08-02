from enum import IntEnum
from img.common import Box
from utils.log import get_logger
from ..common import ark_intf

intf = ark_intf

logger = get_logger('Base')

LEAVE = 'base/是否确认离开罗德岛基建.png'
VIEW_SHIFT = 'base/进驻总览.png'
TODO = 'base/待办.png'
TODO_LIST = [f'base/{event}.png' for event in ['可收获', '订单交付', '干员信赖']]
TODO_BLANK = Box((1020, 534), (1260, 654))
DRONE_RECO_BOX = Box.from_size((767, 22), (48, 26))


class Status(IntEnum):
    Unknown = -1
    Big = 0
    Small = 1
    Todo_shown = 2


Status_Pivot = {
    Status.Todo_shown: 'base/待办事项.png',
    Status.Big: ['base/控制中枢-1.png', 'base/贸易站-1.png',
                 'base/制造站-1.png', 'base/发电站-1.png', ],
    Status.Small: ['base/控制中枢-2.png', 'base/贸易站-2.png',
                   'base/制造站-2.png', 'base/发电站-2.png', ],
}


def get_base_status() -> Status:
    scr = intf.screen()
    for status, pivot in Status_Pivot.items():
        if isinstance(pivot, str):
            pivot = [pivot]
        if any(intf.img_match(img, scr) for img in pivot):
            return status
    return Status.Unknown
