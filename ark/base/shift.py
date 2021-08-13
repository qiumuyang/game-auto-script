from typing import Callable, Iterable
from copy import deepcopy
from utils.interface import Direct
from .data import *
from .reco import move_to_shift_top, reco_current_operators, reco_current_rooms, reco_manu_index, reco_product_name
from .shift_data import *

CONFIRM = 'base/确认.png'
CLEAR_SELECT = 'base/清空选择.png'
MANU_ENTRANCE_BOX = Box.from_size((288, 595), (85, 79))
MOOD_THRESH = 12


def _select_operators(names: Iterable[str]) -> None:
    # a selection is always after a recognition
    # reco: from left to right
    # select: from right to left
    logger.info('选择干员: ' + ', '.join(names))
    name_set = set(names)

    prev_scr = intf.screen()
    while name_set:
        for op in reco_current_operators():
            if op.name in name_set:
                name_set.remove(op.name)
                intf.tap(op.entrance)
                time.sleep(0.5)
            if not name_set:
                # done
                return

        intf.swipe(Direct.Left, src=(400, 360), duration=300)
        time.sleep(1.6)

        scr = intf.screen()
        if intf.img_cmp(prev_scr, scr):
            # already come to the leftmost
            logger.error('选择干员失败: ' + ', '.join(name_set))
            return
        prev_scr = scr


def _reco_filtered_operators(filt_cond: Callable[[Operator], bool],
                             max_swipe: int = 5,
                             capacity: int = None,
                             brk_cond: Callable[[List[Operator]], bool] = None) -> List[str]:
    # recognize operators that meet 'filt_cond' up to 'capacity'
    # quit after 'max_swipe' or meeting 'brk_cond'
    # will remain the origin position when return
    intf.swipe_until_stable(Direct.Left)

    names = set()
    swipe = 0
    while 1:
        operators = reco_current_operators()
        if brk_cond is not None and brk_cond(operators):
            break
        for operator in operators:
            if filt_cond(operator):
                names.add(operator.name)
            if capacity is not None and len(names) == capacity:
                break
        if capacity is not None and len(names) == capacity:
            break
        if swipe >= max_swipe:
            break
        intf.swipe(Direct.Right, src=(400, 360), duration=300)
        swipe += 1
        time.sleep(1)
    return list(names)


def _shift_rest_brk(operators: List[Operator]) -> bool:
    return all(op.mood == MAX_MOOD for op in operators)


def _shift_rest_filt(operator: Operator) -> bool:
    return operator.mood != MAX_MOOD and not operator.on_shift


def _shift_rest(current: List[Operator]) -> None:
    names = _reco_filtered_operators(
        _shift_rest_filt, capacity=5, brk_cond=_shift_rest_brk)

    if not names or set(names) == set(op.name for op in current):
        logger.info(f'{ShiftType.Rest.value} 无需换班')
        intf.img_tap(BACK, 1)
        return

    _select_operators(names)

    # confirm shift
    while intf.img_match(CONFIRM):
        intf.img_tap(CONFIRM, 1)


def _get_current_operators(type: ShiftType) -> List[Operator]:
    if type == ShiftType.Rest:
        cnt = 5
        def judge(op: Operator): return op.on_rest
    elif type not in ShiftOperator:
        return []
    else:
        cnt = len(ShiftOperator[type][0])
        def judge(op: Operator): return op.on_shift
    return [op for op in reco_current_operators()[:cnt] if judge(op)]


def _shift_work_filt(operator: Operator) -> bool:
    return operator.mood == MAX_MOOD and not operator.on_shift


def _shift(entrance: Box, type: ShiftType) -> None:
    intf.tap(entrance)
    while not intf.wait_img([CONFIRM, CLEAR_SELECT], 5):
        logger.error('等待干员工作详情页')

    intf.swipe_until_stable(Direct.Left)
    intf.img_tap(CLEAR_SELECT, 1)  # clear selection for recognition

    current_operators: List[Operator] = _get_current_operators(type)
    logger.info(f'换班: {type.value}, 当前: {current_operators}')
    if type == ShiftType.Rest:
        _shift_rest(current_operators)
        return
    else:
        if any(op.mood < MOOD_THRESH for op in current_operators) \
                or len(current_operators) < len(ShiftOperator[type][0]):
            # need shift
            candidates = deepcopy(ShiftOperator[type])
            if type in [ShiftType.ProductGold, ShiftType.ProductRecord]:
                candidates.extend(ShiftOperator[ShiftType.ProductAny])
            free_operators = _reco_filtered_operators(_shift_work_filt)
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


def do_manufacture_shift() -> None:
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
            # has come to the bottom
            break
        prev = current

        for room in current:
            shift_type = ShiftMapping.get(room.name, None)
            if not shift_type:
                continue

            if shift_type == ShiftType.Rest \
                    and (any(op.mood == MAX_MOOD
                             for op in room.attendance)  # exists max mood op
                         or len(room.attendance) != room.capacity):          # not full
                pass
            elif shift_type != ShiftType.Rest and \
                    any(op.mood < MOOD_THRESH
                        for op in room.attendance):
                pass
            else:
                logger.info(f'{shift_type.value} 无需换班')
                continue

            _shift(room.entrance, shift_type)

        time.sleep(2)
        intf.swipe(Direct.Down, (600, 200), distance=350)
        time.sleep(2)
