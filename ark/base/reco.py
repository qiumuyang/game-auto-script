from utils.interface import Direct
from typing import List, Tuple
from .data import *
from .shift_data import *
from img.reco import recognize
from img.utils import binarization
import re


def reco_room_title() -> Tuple[str, str]:
    if get_base_status() == Status.Room:
        title = recognize(intf.screen(box=ROOM_TITLE_BOX))
        match = re.search(r'[^a-zA-Z0-9]+', title)
        if match and match.group(0) in ROOM_NAMES:
            name = match.group(0)
            suffix = title.strip(name)
            return name, suffix
    return '', ''


def reco_manu_index(box: Box) -> str:
    img = binarization(ark_intf.screen(box=box), 127)
    return recognize(img, repl={'亿': '0', 'O': '0'})


def reco_product_name() -> str:
    product = ''
    if get_base_status() == Status.Manu:
        product_img = intf.screen(box=PRODUCT_RECO_BOX)
        product = recognize(binarization(product_img, 165))
    else:
        logger.warning('未处于制造站界面识别产品')
    return product


def move_to_shift_top() -> None:
    assert(get_base_status() == Status.Shift)
    while 1:
        rooms = reco_current_rooms()
        if rooms and rooms[0].name == '控制中枢':
            break
        intf.swipe(Direct.Up, (600, 600))
        time.sleep(0.5)


def reco_current_rooms() -> List[Room]:
    scr = intf.screen()
    rooms = []
    for box in intf.img_match(ROOM_PIVOT, scr, thresh=0.9):
        p0 = box.x0 + ROOM_X_OFFSET, box.y0 + ROOM_Y_OFFSET
        room = Room.from_coordinate(p0)
        if room:
            rooms.append(room)
    return rooms


def reco_all_rooms() -> List[Room]:
    move_to_shift_top()

    ret: List[Room] = []
    prev = []
    while 1:
        current = reco_current_rooms()
        if current == prev:
            break
        prev = current

        logger.debug(' | '.join([room.verbose for room in current]))
        for room in current:
            for recent in ret[-3:]:
                if intf.img_cmp(room.img, recent.img, thresh=7):
                    # is recognized before
                    break
            else:
                ret.append(room)

        intf.swipe(Direct.Down, (600, 200))
        time.sleep(2)

    return ret
