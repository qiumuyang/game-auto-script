from adb.adb import Key
from .data import *

TimeLasting = None
alpha = 0.125


def handle_single_battle() -> bool:
    global TimeLasting
    start_tm = time.time()

    # check current scene
    prompt = True
    while not is_battle_prev_scene():
        if intf.img_match('battle/map_pivot.png') or \
                intf.img_match('battle/enemy_pivot.png') or \
                intf.img_match('battle/全员信赖.png'):
            intf.keyevent(Key.BACK)
            time.sleep(2)
        if prompt:
            logger.info('等待关卡界面')
            prompt = False
        time.sleep(1)

    # check prts
    img, prts = get_prts_status()
    if prts == PRTS.Locked:
        logger.error('代理指挥未解锁')
        return False
    while prts == PRTS.Disabled:
        logger.info('启用代理指挥')
        intf.img_tap(img[PRTS.Disabled.value])
        time.sleep(1)
        img, prts = get_prts_status()

    san, m_san, cost = get_sanity()
    logger.info(f'理智: {san}/{m_san}')
    logger.info(f'理智消耗: {cost}')
    if san < cost:
        logger.info('理智不足')
        return False
    if TimeLasting is not None:
        logger.info(f'预计所需时间 {round(san // cost * TimeLasting / 60)} min')

    # start
    logger.debug('开始行动[关卡]')
    while 1:
        match = intf.wait_img([START_BATTLE_1_1, START_BATTLE_1], 3)
        if match:
            intf.img_tap(match)
            break
    # intf.img_tap(START_BATTLE_1)
    logger.debug('开始行动[队伍]')
    intf.img_tap(START_BATTLE_2)

    # on enter
    intf.wait_img(PRTS_PROPER)
    if intf.img_match(SPEED_1):
        intf.img_tap(SPEED_1)
        logger.info('设置关卡二倍速')

    logger.info('等待关卡结束')
    while 1:
        if any(intf.img_match(pivot)
               for pivot in END_BATTLE):
            logger.debug([intf.img_match(pivot)
                          for pivot in END_BATTLE])
            break
        elif intf.img_match(SPEED_2) and intf.img_match(PRTS_FAIL):
            logger.error('代理指挥失败')
            return False

    # TODO: level up detect
    logger.info('关卡结束')
    time.sleep(2)

    ret = False
    if is_battle_end_success():
        while any(intf.img_match(pivot)
                  for pivot in END_BATTLE):
            time.sleep(1)
            intf.tap(BLANK_BOX)
    ret = True

    cost_time = round(time.time() - start_tm)
    if TimeLasting is None:
        TimeLasting = cost_time
    else:
        TimeLasting = round((1 - alpha) * TimeLasting + alpha * cost_time)
    logger.info(f'用时{cost_time}s')
    return ret


def execute_single_level():
    cnt = 0
    while 1:
        cnt += 1
        logger.info(f'第{cnt}次战斗')
        if not handle_single_battle():
            break
