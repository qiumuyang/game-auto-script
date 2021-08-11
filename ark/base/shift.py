from utils.interface import Direct
from .data import *
from .reco import move_to_shift_top, reco_current_rooms, reco_manu_index, reco_product_name, reco_room_title
from .shift_data import *

CONFIRM = 'base/确认.png'
CLEAR_SELECT = 'base/清空选择.png'
MANU_ENTRANCE_BOX = Box.from_size((288, 595), (85, 79))
MOOD_THRESH = 12


def _shift(entrance: Box, type: ShiftType) -> None:
    intf.tap(entrance)
    while not intf.wait_img([CONFIRM, CLEAR_SELECT], 5):
        logger.error('等待干员工作详情页')
    intf.swipe_until_stable(Direct.Left)
    intf.img_tap(CLEAR_SELECT, 1)

    # TODO recognize mood & name
    current_operators: List[Operator] = []  # get_current_op()
    if type == ShiftType.Rest:
        pass
    else:
        if any(op.mood < MOOD_THRESH for op in current_operators):
            # need shift
            candidates = ShiftOperator[type].copy()
            if type in [ShiftType.ProductGold, ShiftType.ProductRecord]:
                candidates.extend(ShiftOperator[ShiftType.ProductAny])
            free_operators: List[str] = []  # get_free_op()
            for opr_list in candidates:
                if all(op in free_operators for op in opr_list):
                    # Select Operators
                    pass
            else:
                logger.error(f'{type.value} 换班失败: 未找到符合条件的干员')
                intf.img_tap(BACK, 1)
                return
        else:
            logger.info(f'{type.value} 无需换班')
            intf.img_tap(BACK, 1)
            return

    # confirm shift
    while intf.img_match(CONFIRM):
        intf.img_tap(CONFIRM, 1)


def do_product_shift() -> None:
    # manufacture station
    move_to_manufacture_station()

    for box in MANU_NUM_RECO_BOX:
        index = reco_manu_index(box)
        if not re.match('[0-9]+', index):
            break
        intf.tap(box)
        time.sleep(1)
        product = reco_product_name()
        logger.info(f'换班: 制造站{index} - {product}')
        if '作战记录' in product:
            _shift(MANU_ENTRANCE_BOX, ShiftType.ProductRecord)
        elif product == '赤金':
            _shift(MANU_ENTRANCE_BOX, ShiftType.ProductGold)
        time.sleep(2)


def do_normal_shift() -> None:
    # TODO add move to shift page
    move_to_shift_top()

    prev = []
    while 1:
        current = reco_current_rooms()
        if current == prev:
            break
        prev = current

        for room in current:
            if room.name == '会客室':
                _shift(room.entrance, ShiftType.Clue)
            elif room.name == '贸易站':
                _shift(room.entrance, ShiftType.Trade)
            elif room.name == '制造站':
                # done separately
                pass
            elif room.name == '宿舍':
                _shift(room.entrance, ShiftType.Rest)
            elif room.name == '办公室':
                _shift(room.entrance, ShiftType.Recruit)

        intf.swipe(Direct.Down, (600, 200))
        time.sleep(2)
