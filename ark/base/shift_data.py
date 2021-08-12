from img.utils import binarization
from adb.adb import COORDINATE_T
from enum import Enum
from typing import List
from PIL import Image
from .data import *


class ShiftType(Enum):
    Rest = '宿舍'
    Clue = '会客室'
    ProductGold = '制造站(赤金)'
    ProductRecord = '制造站(作战记录)'
    ProductAny = '制造站'
    Trade = '贸易站'
    Recruit = '办公室'


# Modify this to change shift
ShiftOperator = {
    ShiftType.Clue: [
        ['陈', '红'],
        ['远山', '星极'],
        ['暗索', '12F'],
    ],
    ShiftType.Trade: [
        ['能天使', '拉普兰德', '德克萨斯'],
        ['空爆', '月见夜', '古米'],
        ['缠丸', '安比尔', '慕斯'],
        ['夜刀', '玫兰莎', '梓兰'],
    ],
    ShiftType.Recruit: [
        ['艾雅法拉'],
        ['酸糖'],
        ['伊桑'],
        ['宴'],
    ],
    ShiftType.ProductGold: [
        ['砾', '夜烟', '斑点'],
        ['芬', '清流', '调香师'],
    ],
    ShiftType.ProductRecord: [
        ['断罪者', '白雪', '红豆'],
        ['Castle-3', '霜叶', '食铁兽'],
        ['红云', '稀音', '刻俄柏'],
    ],
    ShiftType.ProductAny: [
        ['异客', '森蚺', '温蒂'],
        ['梅尔', '赫默', '白面鸮'],
        ['史都华德', '杰西卡', '香草'],
    ],
}


def reco_mood(mood_img: Image.Image) -> int:
    mood = binarization(mood_img, 200)
    w, h = mood.size
    for x in range(w):
        # reach first black
        if mood.getpixel((x, 0)) == (0, 0, 0):
            break
    return round(MAX_MOOD * x / w)


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
            self.mood = reco_mood(intf.img_crop(
                opr_img, OPERATOR_OVERVIEW_MOOD_BOX))

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

    @property
    def capacity(self) -> int:
        return len(self.operators)

    @property
    def attendance(self) -> List[OperatorOverview]:
        return [op for op in self.operators if not op.empty]

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


class Operator:
    NameBox = Box.from_size((36, 246), (90, 28))
    MoodBox = Box.from_size((32, 242), (84, 2))

    def __init__(self, img: Image.Image, entrance: Box) -> None:
        self.mood = reco_mood(intf.img_crop(img, self.MoodBox))
        self.name = recognize(binarization(
            intf.img_crop(img, self.NameBox), 100))
        self.on_shift = not not intf.img_match('base/工作中.png', img)
        self.on_rest = not not intf.img_match('base/休息中.png', img)
        self.entrance = entrance

    def __repr__(self) -> str:
        return f'({self.name} {self.mood}{" 工作中" if self.on_shift else ""}{" 休息中" if self.on_rest else ""})'
