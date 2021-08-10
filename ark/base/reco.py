from PIL import Image
from typing import Tuple
from .data import *
from img.reco import recognize
from img.utils import binarization
import re


class Operator:
    __Normal = 0
    __Empty = 1
    __Invalid = 2

    def __init__(self, opr_img: Image.Image) -> None:
        self.__status = self.__Normal
        self.img = None
        self.mood = None
        if intf.img_cmp(opr_img, OPERATOR_EMPTY, thresh=5):
            self.__status = self.__Empty
        elif intf.img_cmp(opr_img, OPERATOR_INVALID, thresh=5):
            self.__status = self.__Invalid
        else:
            self.img = opr_img.copy()
            # recognize mood
            self.mood = Operator.get_operator_mood(opr_img)

    @staticmethod
    def get_operator_mood(opr_img: Image.Image) -> int:
        mood = intf.img_crop(opr_img, OPERATOR_MOOD_BOX)
        mood = binarization(mood, 200)
        w, h = mood.size
        for x in range(w):
            # reach first black
            if mood.getpixel((x, 0)) == (0, 0, 0):
                break
        return round(MAX_MOOD * x / w)

    @property
    def valid(self):
        return self.__status != self.__Invalid

    @property
    def empty(self):
        return self.__status == self.__Empty


class Room:
    def __init__(self, name: str) -> None:
        self.name = name
        self.operators = []

    @staticmethod
    def from_image(room_img: Image.Image):
        for bbox in ROOM_NAME_BOXES:
            room_name_img = intf.img_crop(room_img, bbox)
            name = recognize(room_name_img)
            if name in ROOM_NAMES:
                break
        else:
            return None

        ret = Room(name)
        for bbox in OPERATOR_RECO_BOX:
            opr_img = intf.img_crop(room_img, bbox)
            opr = Operator(opr_img)
            if opr.valid:
                ret.operators.append(opr)
        return ret

    def __repr__(self) -> str:
        return f'{self.name}: {sum(not x.empty for x in self.operators)}/{len(self.operators)}'


def reco_room_title() -> Tuple[str, str]:
    if get_base_status() == Status.Room:
        title = recognize(intf.screen(box=ROOM_TITLE_BOX))
        match = re.search(r'[^a-zA-Z0-9]+', title)
        if match and match.group(0) in ROOM_NAMES:
            name = match.group(0)
            suffix = title.strip(name)
            return name, suffix
    return '', ''


def reco_current_rooms():
    scr = intf.screen()
    for box in intf.img_match(ROOM_PIVOT, scr, thresh=0.95):
        p0 = box.x0 + ROOM_X_OFFSET, box.y0 + ROOM_Y_OFFSET
        room_image = intf.screen(cached=True, box=Box.from_size(p0, ROOM_SIZE))
        room = Room.from_image(room_image)
