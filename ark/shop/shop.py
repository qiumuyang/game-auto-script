from adb.adb import Key
import logging
import time
from typing import List
from .data import *

logger = logging.getLogger('Store')
logger.setLevel(logging.DEBUG)


def reco_items() -> List[ShopItem]:
    items = []
    logger.info('信用商店识别结果：')
    for box in SHOP_ITEM_BOX:
        item_img = ark_intf.screen(box=box)
        item = ShopItem.from_image(item_img)
        items.append(item)
        logger.info(f'  {item}')
    return items


def _purchase_item(i: int):
    assert(0 <= i < len(SHOP_ITEM_BOX))
    purchased = False
    while 1:
        status = get_shop_status()
        if status == Status.Unknown:
            pass
        elif status == Status.Other_shop:
            logger.debug('切换信用商店界面')
            intf.tap(SHOP_BOX_DICT['信用交易所'])
        elif status == Status.Credit_shop:
            if not purchased:
                # enter item page
                intf.tap(SHOP_ITEM_BOX[i])
            else:
                # already back to shop page
                logger.debug('购买完成')
                return
        elif status == Status.Purchase:
            logger.debug('购买商品')
            intf.img_tap(PURCHASE, 1)
        elif status == Status.Not_enough:
            logger.error('信用不足')
            purchased = True
            intf.keyevent(Key.BACK)
        elif status == Status.Get:
            logger.debug('获得物资')
            purchased = True
            intf.tap(GET_AWARD_BOX)
        time.sleep(1.5)


def execute_purchase() -> None:
    # TODO: add move-to-shop
    while get_shop_status() == Status.Other_shop:
        intf.tap(SHOP_BOX_DICT['信用交易所'])

    assert(get_shop_status() == Status.Credit_shop)

    credit = reco_credit()
    items = reco_items()
    logger.info(f'当前信用 {credit}')

    for i, item in enumerate(items):
        if item.out_of_stock:
            continue
        elif item.name in EXCEPT_ITEM:
            continue
        elif item.cost <= credit:
            # able to purchase
            if credit <= MAX_CREDIT and not item.discount:
                continue
            else:
                _purchase_item(i)
                logger.info(f'购买[{item.name}]')
                assert(get_shop_status() == Status.Credit_shop)
                assert(credit - item.cost == reco_credit())
                credit -= item.cost
                logger.info(f'当前信用 {credit}')
