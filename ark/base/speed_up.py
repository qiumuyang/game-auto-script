from .data import *
from .reco import reco_product_name, recognize
import time


def manufacture_speed_up() -> None:
    logger.info('消耗无人机加速制造')
    move_to_manufacture_station()

    product = reco_product_name()
    for img in ['base/加速.png', 'base/最多.png', 'base/确定.png', 'base/收取.png']:
        intf.img_tap(img, 1)
        time.sleep(1.5)
        if img == 'base/最多.png':
            num = recognize(intf.screen(box=SPEED_UP_COUNT_RECO_BOX))
            logger.info(f'协助制造 {product} {num} 份')
