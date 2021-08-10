from ark.nav.navigate import move_to_base
from .data import *
from .reco import reco_room_title, recognize, binarization
import time

manufactures = ['base/制造站-1.png', 'base/制造站-2.png']
product_box = Box.from_size((23, 554), (115, 115))
reco_speed_box = Box.from_size((857, 440), (51, 34))
reco_product_box = Box.from_size((1039, 236), (168, 38))


def _speed_up():
    product_img = intf.screen(box=reco_product_box)
    product = recognize(binarization(product_img, 165))
    for img in ['base/加速.png', 'base/最多.png', 'base/确定.png', 'base/收取.png']:
        intf.img_tap(img, 1)
        time.sleep(1.5)
        if img == 'base/最多.png':
            incr = recognize(intf.screen(box=reco_speed_box))
            logger.info(f'协助制造 {product} {incr} 份')


def manufacture_speed_up() -> None:
    logger.info('消耗无人机加速制造')
    assert(get_base_status() in [Status.MainBig, Status.MainSmall])
    while 1:
        status = get_base_status()
        if status in [Status.MainBig, Status.MainSmall]:
            for icon in manufactures:
                if intf.img_tap(icon, 1):
                    break
            else:
                logger.info('加速失败：未找到制造站')
                return
        elif status == Status.Room:
            name, suffix = reco_room_title()
            if name != '制造站':
                intf.img_tap(BACK, 1)
            else:
                intf.tap(product_box)
        elif status == Status.Manu:
            _speed_up()
            break
        time.sleep(1.5)
