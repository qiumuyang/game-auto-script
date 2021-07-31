import time
from typing import Tuple
from img.common import Box
from img.reco import recognize
from enum import IntEnum
from ..common import ark_intf

intf = ark_intf


class PRTS(IntEnum):
    Unknown = -1
    Enabled = 0
    Disabled = 1
    Locked = 2


PRTS_img_box = [((1041, 566), (1249, 619)),
                ((1043, 568), (1247, 616)),
                ((1041, 567), (1249, 619))]
PRTS_img = [f'battle/代理指挥-{i}.png' for i in [1, 2, 3]]


def __get_prts_diff(status: PRTS) -> int:
    value = status.value
    p0, p1 = PRTS_img_box[value]
    img = PRTS_img[value]
    return intf.img_diff(intf.screen(box=Box(p0, p1)), img)


def get_prts_status() -> PRTS:
    diff_dict = {status: __get_prts_diff(status)
                 for status in [PRTS.Enabled, PRTS.Disabled, PRTS.Locked]}
    min_diff = min(diff_dict.items(), key=lambda t: t[1])
    status, diff = min_diff
    return status if diff < 4 else PRTS.Unknown


Sanity_box = Box.from_size((1115, 13), (158, 45))
Sanity_cost_box = Box.from_size((1182, 676), (44, 23))
Pivot_img = ['battle/san.png',
             'battle/开始行动-1.png']


def get_sanity() -> Tuple[int, int, int]:
    san_img = intf.screen(box=Sanity_box)
    san_str = recognize(san_img, repl={'g': '9'})
    san_cost_img = intf.screen(box=Sanity_cost_box)
    san_cost_str = recognize(san_cost_img)
    if '/' not in san_str or not san_cost_str.startswith('-'):
        return -1, -1, -1
    cur, max = san_str.split('/')
    cur = int(cur) if cur.isdigit() else -1
    max = int(max) if max.isdigit() else -1
    cost = san_cost_str[1:]
    cost = int(cost) if cost.isdigit() else -1
    return cur, max, cost


def is_battle_prev_scene() -> bool:
    return any(len(intf.img_match(pivot)) > 0 for pivot in Pivot_img)


START_BATTLE_1 = 'battle/开始行动-1.png'
START_BATTLE_1_BOX = Box((1121, 642), (1230, 672))
START_BATTLE_2 = 'battle/开始行动-2.png'
START_BATTLE_2_BOX = Box((1040, 371), (1165, 639))
PRTS_PROPER = 'battle/代理指挥作战正常运行中.png'
SPEED_1 = 'battle/speed-1.png'
END_SPECIAL = 'battle/剿灭结束.png'
END_BATTLE = ['battle/全员信赖.png', 'battle/行动结束.png', END_SPECIAL]
END_BATTLE_TEXT_BOX = Box((34, 582), (397, 672))
BLANK_BOX = Box((938, 317), (1272, 427))
BLANK_BOX_2 = Box((873, 92), (1259, 221))  # 剿灭
STAR = 'battle/star.png'
# P_1 = 'battle/本次行动配置不可更改.png'


def is_battle_end_success() -> bool:
    if intf.img_match(END_SPECIAL):
        # 剿灭
        intf.tap(BLANK_BOX_2)
        time.sleep(1)
        return recognize(intf.screen(box=END_BATTLE_TEXT_BOX)) == '行动结束'
    else:
        return recognize(intf.screen(box=END_BATTLE_TEXT_BOX)) == '行动结束' \
            and len(intf.img_match(STAR)) == 3  # 3-star
