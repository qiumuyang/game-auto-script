from typing import Iterable
from utils.interface import Direct
from .data import *
from .reco import move_to_shift_top, reco_current_operators, reco_current_rooms, reco_manu_index, reco_product_name
from .shift_data import *

CONFIRM = 'base/确认.png'
CLEAR_SELECT = 'base/清空选择.png'
MANU_ENTRANCE_BOX = Box.from_size((288, 595), (85, 79))
MOOD_THRESH = 12


def _select_operators(names: Iterable[str]) -> None:
    logger.info('选择干员: ' + ', '.join(names))
    name_set = set(names)
    intf.swipe_until_stable(Direct.Left)
    swipe = 0
    while name_set:
        for op in reco_current_operators():
            if op.name in name_set:
                name_set.remove(op.name)
                intf.tap(op.entrance)
                time.sleep(0.5)
            if not name_set:
                break
        intf.swipe(Direct.Right, src=(400, 360), duration=300)
        time.sleep(2)
        swipe += 1
        if swipe >= 10:
            logger.error('选择干员失败: ' + ', '.join(name_set))
            return


def _select_rest() -> None:
    # First, select operators
    select = set()
    swipe = 0
    while swipe < 5 and len(select) < 5:
        for op in reco_current_operators():
            if op.mood != MAX_MOOD and not op.on_shift:
                select.add(op.name)
            if len(select) == 5:
                break
        intf.swipe(Direct.Right, src=(400, 360), duration=300)
        swipe += 1
        time.sleep(2)

    # Next, choose operators
    _select_operators(select)


def _get_working_operators(type: ShiftType) -> List[Operator]:
    if type not in ShiftOperator:
        return []
    cnt = len(ShiftOperator[type][0])
    return [op for op in reco_current_operators()[:cnt] if op.on_shift]


def _get_free_operators() -> List[str]:
    intf.swipe_until_stable(Direct.Left)
    free = set()
    swipe = 0
    while swipe < 3:
        for op in reco_current_operators():
            if op.mood == MAX_MOOD and not op.on_shift:
                free.add(op.name)
        intf.swipe(Direct.Right, src=(400, 360), duration=300)
        swipe += 1
        time.sleep(2)
    return list(free)


def _shift(entrance: Box, type: ShiftType) -> None:
    intf.tap(entrance)
    while not intf.wait_img([CONFIRM, CLEAR_SELECT], 5):
        logger.error('等待干员工作详情页')
    intf.swipe_until_stable(Direct.Left)
    intf.img_tap(CLEAR_SELECT, 1)

    working_operators: List[Operator] = _get_working_operators(type)
    logger.info(f'换班: {type.value}, 当前: {working_operators}')

    if type == ShiftType.Rest:
        _select_rest()
    else:
        if any(op.mood < MOOD_THRESH for op in working_operators):
            # need shift
            candidates = ShiftOperator[type].copy()
            if type in [ShiftType.ProductGold, ShiftType.ProductRecord]:
                candidates.extend(ShiftOperator[ShiftType.ProductAny])
            free_operators: List[str] = _get_free_operators()
            for opr_list in candidates:
                if all(op in free_operators for op in opr_list):
                    _select_operators(opr_list)
                    break
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
        if '作战记录' in product:
            _shift(MANU_ENTRANCE_BOX, ShiftType.ProductRecord)
        elif product == '赤金':
            _shift(MANU_ENTRANCE_BOX, ShiftType.ProductGold)
        time.sleep(2)


def do_normal_shift() -> None:
    move_to_main_base()
    while get_base_status() != Status.Shift:
        intf.img_tap(VIEW_SHIFT, 1)
        time.sleep(0.5)
    move_to_shift_top()

    prev = []
    while 1:
        current = reco_current_rooms()
        if current == prev:
            break
        prev = current

        for room in current:
            if room.name == '会客室':
                if any(op.mood < MOOD_THRESH for op in room.attendance):
                    _shift(room.entrance, ShiftType.Clue)
            elif room.name == '贸易站':
                if any(op.mood < MOOD_THRESH for op in room.attendance):
                    _shift(room.entrance, ShiftType.Trade)
            elif room.name == '制造站':
                # done separately
                pass
            elif room.name == '宿舍':
                # if all op are not max mood, do nothing
                if any(op.mood == MAX_MOOD for op in room.attendance) \
                        or len(room.attendance) != room.capacity:
                    _shift(room.entrance, ShiftType.Rest)
            elif room.name == '办公室':
                if any(op.mood < MOOD_THRESH for op in room.attendance):
                    _shift(room.entrance, ShiftType.Recruit)

        time.sleep(2)
        intf.swipe(Direct.Down, (600, 200))
        time.sleep(2)
