from .data import *
import logging
import time


logger = logging.getLogger('Battle')
logger.setLevel(logging.DEBUG)


def handle_single_battle() -> bool:
    # check current scene
    prompt = True
    while not is_battle_prev_scene():
        if prompt:
            logger.info('等待关卡界面')
            prompt = False
        time.sleep(1)

    # check prts
    prts = get_prts_status()
    if prts == PRTS.Locked:
        logger.error('代理指挥未解锁')
        return False
    while prts == PRTS.Disabled:
        logger.info('启用代理指挥')
        intf.img_tap(PRTS_img[PRTS.Disabled.value])
        time.sleep(1)
        prts = get_prts_status()

    san, m_san, cost = get_sanity()
    logger.info(f'理智: {san}/{m_san}')
    logger.info(f'理智消耗: {cost}')
    if san < cost:
        logger.info('理智不足')
        return False

    # start
    logger.debug('开始行动[关卡]')
    intf.img_tap(START_BATTLE_1)
    logger.debug('开始行动[队伍]')
    intf.img_tap(START_BATTLE_2)

    # on enter
    intf.wait_img(IN_BATTLE)
    if intf.img_match(SPEED_1):
        intf.img_tap(SPEED_1)
        logger.info('设置关卡二倍速')

    logger.info('等待关卡结束')
    end = intf.wait_img(END_BATTLE)
    if end == END_SPECIAL:
        intf.tap(Box((1124, 9), (1268, 56)))

    # TODO: prts failure detect
    #       level up detect
    logger.info('关卡结束')
    time.sleep(5)

    if is_battle_end_success():
        intf.tap(BLANK_BOX)
        return True

    return False


def execute_single_level():
    cnt = 0
    while 1:
        cnt += 1
        logger.info(f'第{cnt}次战斗')
        if not handle_single_battle():
            break
