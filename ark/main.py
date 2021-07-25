import logging
from .battle.battle import handle_single_battle

logging.basicConfig(format="[%(levelname)s] %(asctime)s %(name)s %(message)s")

logger = logging.getLogger('Main')
logger.setLevel(logging.INFO)


def execute_single_level():
    cnt = 0
    while handle_single_battle():
        cnt += 1
        logger.info(f'第{cnt}次战斗')
