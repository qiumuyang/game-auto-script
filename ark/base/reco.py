from adb.adb import COORDINATE_T
from utils.interface import Direct
from PIL import Image
from typing import List, Tuple
from .data import *
from img.reco import recognize
from img.utils import binarization
import re


class OperatorOverview:
    __Normal = 0
    __Empty = 1
    __Invalid = 2

    def __init__(self, opr_img: Image.Image) -> None:
        self.__status = self.__Normal
        self.img = None
        self.mood = 0
        if intf.img_cmp(opr_img, OPERATOR_EMPTY, thresh=8):
            self.__status = self.__Empty
        elif intf.img_cmp(opr_img, OPERATOR_INVALID, thresh=8):
            self.__status = self.__Invalid
        else:
            self.img = opr_img.copy()
            # recognize mood
            self.mood = OperatorOverview.get_operator_mood(opr_img)

    @staticmethod
    def get_operator_mood(opr_img: Image.Image) -> int:
        mood = intf.img_crop(opr_img, OPERATOR_OVERVIEW_MOOD_BOX)
        mood = binarization(mood, 200)
        w, h = mood.size
        for x in range(w):
            # reach first black
            if mood.getpixel((x, 0)) == (0, 0, 0):
                break
        return round(MAX_MOOD * x / w)

    @property
    def valid(self) -> bool:
        return self.__status != self.__Invalid

    @property
    def empty(self) -> bool:
        return self.__status == self.__Empty


class Room:
    def __init__(self, name: str, img: Image.Image, entrance: Box) -> None:
        self.name = name
        self.operators: List[OperatorOverview] = []
        self.img = img.copy()
        self.entrance = entrance

    @staticmethod
    def from_coordinate(coordinate: COORDINATE_T):
        room_img = intf.screen(
            cached=True, box=Box.from_size(coordinate, ROOM_SIZE))
        for bbox in ROOM_NAME_BOXES:
            room_name_img = intf.img_crop(room_img, bbox)
            name = recognize(room_name_img)
            if name in ROOM_NAMES:
                break
        else:
            logger.debug(f'room name no match: {name}')
            return None

        entrance = coordinate[0] + OPERATOR_OVERVIEW_TAP_BOX[0].x0, \
            coordinate[1] + OPERATOR_OVERVIEW_TAP_BOX[0].y0
        print(entrance)
        ret = Room(name, room_img, Box.from_size(
            entrance, OPERATOR_OVERVIEW_TAP_BOX[0].size))
        for bbox in OPERATOR_OVERVIEW_RECO_BOX:
            opr_img = intf.img_crop(room_img, bbox)
            opr = OperatorOverview(opr_img)
            if opr.valid:
                ret.operators.append(opr)
        return ret

    def __repr__(self) -> str:
        return f'{self.name}: {sum(not x.empty for x in self.operators)}/{len(self.operators)}'

    @property
    def verbose(self) -> str:
        mood_str = ' '.join([str(op.mood)
                            for op in self.operators if not op.empty])
        room_str = f'{self.name}: {sum(not x.empty for x in self.operators)}/{len(self.operators)}'
        return room_str if not mood_str else room_str + ': ' + mood_str

    def __eq__(self, o: object) -> bool:
        assert(isinstance(o, Room))
        return self.name == o.name and len(self.operators) == len(o.operators) \
            and all(self.operators[i].mood == o.operators[i].mood for i, op in enumerate(self.operators))


def reco_room_title() -> Tuple[str, str]:
    if get_base_status() == Status.Room:
        title = recognize(intf.screen(box=ROOM_TITLE_BOX))
        match = re.search(r'[^a-zA-Z0-9]+', title)
        if match and match.group(0) in ROOM_NAMES:
            name = match.group(0)
            suffix = title.strip(name)
            return name, suffix
    return '', ''


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
