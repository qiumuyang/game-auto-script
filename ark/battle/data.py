import time
from enum import IntEnum
from typing import List, Tuple

from img.common import Box
from img.reco import recognize
from img.utils import binarization
from utils.log import get_logger
from ..common import ark_intf

intf = ark_intf
logger = get_logger('Battle', 'INFO')


class PRTS(IntEnum):
    Unknown = -1
    Enabled = 0
    Disabled = 1
    Locked = 2


PRTS_LIST = [PRTS.Enabled, PRTS.Disabled, PRTS.Locked]
PRTS_img_box = Box((1041, 583), (1246, 629))
PRTS_img = [f'battle/代理指挥-{i}.png' for i in [1, 2, 3]]
PRTS_img_box2 = Box((1069, 568), (1229, 593))
PRTS_img2 = [f'battle/代理指挥-{i}-1.png' for i in [1, 2, 3]]
PRTS_THRESH = 4
BIN_THRESH = 120


def get_prts_match_result(box: Box, images: List[str], binary: bool = False) -> List[float]:
    distance = [0.0] * 3
    scr = intf.screen(box=box)
    if binary:
        scr = binarization(scr, BIN_THRESH)
    for status in [PRTS.Enabled, PRTS.Disabled, PRTS.Locked]:
        idx = status.value
        if binary:
            target = binarization(intf.load_image(images[idx]), BIN_THRESH)
        else:
            target = images[idx]
        distance[idx] = intf.img_diff(scr, target)
    return distance


def get_prts_status() -> Tuple[List[str], PRTS]:
    dist1 = get_prts_match_result(PRTS_img_box, PRTS_img)
    dist2 = get_prts_match_result(PRTS_img_box2, PRTS_img2, binary=True)

    idx1, dist1 = min(enumerate(dist1), key=lambda t: t[1])
    idx2, dist2 = min(enumerate(dist2), key=lambda t: t[1])
    if dist1 > PRTS_THRESH and dist2 > PRTS_THRESH:
        return [], PRTS.Unknown
    if dist1 < dist2:
        return PRTS_img, PRTS_LIST[idx1]
    else:
        return PRTS_img2, PRTS_LIST[idx2]


# Sanity_box = Box.from_size((1115, 13), (158, 45))
Sanity_box = Box.from_size((1115, 20), (148, 37))
Sanity_box2 = Box.from_size((1100, 28), (120, 37))
# Sanity_cost_box = Box.from_size((1182, 676), (44, 23))
Sanity_cost_box = Box.from_size((1184, 689), (43, 26))
Sanity_cost_box2 = Box.from_size((1181, 654), (40, 24))
Pivot_img = ['battle/san.png',
             'battle/开始行动-1.png']


def get_sanity() -> Tuple[int, int, int]:
    san_img = intf.screen(box=Sanity_box)
    san_str = recognize(san_img, repl={'g': '9'})
    san_cost_img = intf.screen(box=Sanity_cost_box)
    san_cost_str = recognize(san_cost_img)
    if '/' not in san_str or not san_cost_str.startswith('-'):
        san_str = recognize(intf.screen(box=Sanity_box2), repl={'g': '9'})
        san_cost_str = recognize(intf.screen(box=Sanity_cost_box2))
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
START_BATTLE_1_1 = 'battle/开始行动-1-1.png'
START_BATTLE_1_BOX = Box((1121, 642), (1230, 672))
START_BATTLE_2 = 'battle/开始行动-2.png'
START_BATTLE_2_BOX = Box((1040, 371), (1165, 639))
PRTS_PROPER = 'battle/代理指挥作战正常运行中.png'
PRTS_FAIL = 'battle/请求人工接管作战.png'
SPEED_1 = 'battle/speed-1.png'
SPEED_2 = 'battle/speed-2.png'
END_SPECIAL = 'battle/剿灭结束.png'
END_BATTLE = ['battle/全员信赖2.png', 'battle/行动结束2.png',
              END_SPECIAL, 'battle/任务失败.png']
# END_BATTLE_TEXT_BOX = Box.from_size((35, 583), (364, 91))
END_BATTLE_TEXT_BOX = Box.from_size((58, 176), (298, 81))
# BLANK_BOX = Box((938, 317), (1272, 427))
BLANK_BOX = Box((1003, 64), (1211, 238))
BLANK_BOX_2 = Box((873, 92), (1259, 221))  # 剿灭
STAR = 'battle/star2.png'


# P_1 = 'battle/本次行动配置不可更改.png'


def is_battle_end_success() -> bool:
    return True
    if intf.img_match(END_SPECIAL):
        # 剿灭
        intf.tap(BLANK_BOX_2)
        time.sleep(1)
        return recognize(intf.screen(box=END_BATTLE_TEXT_BOX)) == '行动结束'
    else:
        return recognize(intf.screen(box=END_BATTLE_TEXT_BOX)) == '行动结束' \
               and len(intf.img_match(STAR, thresh=0.7)) == 3  # 3-star
