from utils.log import get_logger
from PIL import Image
from enum import IntEnum
from img.common import Box
from ..common import ark_intf
from img.reco import recognize
from img.utils import binarization

intf = ark_intf

logger = get_logger('Store', 'INFO')

OUT_OF_STOCK = 'shop/售罄.png'
PURCHASE = 'shop/购买物品.png'
SHOP = ['可露希尔推荐', '源石交易所', '组合包', '时装商店', '凭证交易所', '家具商店', '信用交易所']
SHOP_BOX = [Box.from_size((i * 183, 85), (182, 43)) for i in range(len(SHOP))]
SHOP_BOX_DICT = dict(zip(SHOP, SHOP_BOX))
SHOP_ITEM_BOX = [Box.from_size(
    (i*253 + 16, j*253 + 148), (237, 237))
    for j in range(2)
    for i in range(5)]
SHOP_ITEM_NAME_BOX = Box.from_size((9, 2), (217, 30))
SHOP_ITEM_DISCNT_BOX = Box.from_size((3, 36), (60, 33))
SHOP_ITEM_CNT_BOX = Box.from_size((103, 150), (56, 23))
SHOP_ITEM_COST_BOX = Box.from_size((10, 197), (217, 30))
GET_CREDIT = 'shop/收取信用.png'
GET_CREDIT_BOX = Box((971, 28), (1068, 50))
CREDIT_RECO_BOX = Box((1155, 26), (1200, 50))
CREDIT_RECO_BOX_2 = [Box.from_size((1158 + i * 14, 26), (17, 26))
                     for i in range(3)]
EXCEPT_ITEM = ['碳', '碳素']
MAX_CREDIT = 300
AWARD_BOX = Box((587, 141), (691, 169))
GET_AWARD_BOX = Box((619, 619), (658, 657))


class Status(IntEnum):
    Unknown = -1
    Credit_shop = 0
    Other_shop = 1
    Purchase = 2
    Not_enough = 3
    Get = 4


Status_pivot = {Status.Credit_shop: ['shop/pivot-1.png', 'shop/pivot-2.png'],
                Status.Other_shop: 'shop/信用交易所.png',
                Status.Purchase: PURCHASE,
                Status.Not_enough: 'shop/信用不足.png',
                Status.Get: '获得物资-1.png',
                }


def get_shop_status() -> Status:
    for status, pivot in Status_pivot.items():
        if isinstance(pivot, str):
            pivot = [pivot]
        if any(intf.img_match(img) for img in pivot):
            return status
    return Status.Unknown


def reco_credit() -> int:
    assert(get_shop_status() == Status.Credit_shop)

    # credit_str = recognize(intf.screen(box=CREDIT_RECO_BOX))
    # if not credit_str.isdigit():
    #     raise ValueError(f'credit {credit_str} is not int')

    credit_str = ''
    for box in CREDIT_RECO_BOX_2:
        scr = intf.screen(cached=True, box=box)
        digit = recognize(scr)
        if digit.isdigit() or len(digit) == 0:
            credit_str += digit
        else:
            credit_str += '0'
            logger.error(f'{digit} is not digit')
    return int(credit_str)


class ShopItem:
    def __init__(self, out_of_stock: bool, name: str, count: int, discount: int, cost: int) -> None:
        self.out_of_stock = out_of_stock
        self.name = name
        self.count = count
        self.discount = discount
        self.cost = cost

    def __repr__(self) -> str:
        if self.out_of_stock:
            return f'{self.name} 售罄'
        ret = f'{self.name}×{self.count}: {self.cost}'
        if self.discount:
            ret += f' [-{self.discount}%]'
        return ret

    @staticmethod
    def from_image(img: Image.Image):
        out_of_stock = not not intf.img_match(OUT_OF_STOCK, img)
        name = recognize(intf.img_crop(img, SHOP_ITEM_NAME_BOX))
        discnt = recognize(intf.img_crop(img, SHOP_ITEM_DISCNT_BOX))
        cnt_img = binarization(intf.img_crop(img, SHOP_ITEM_CNT_BOX), 175)
        cost_img = binarization(intf.img_crop(img, SHOP_ITEM_COST_BOX), 210)
        cost = recognize(cost_img)
        cnt = recognize(cnt_img)

        discnt = int(discnt[1:-1]) if discnt[1:-1].isdigit() else 0
        cnt = int(cnt) if cnt.isdigit() else 1
        cost = int(cost) if cost.isdigit() else 1000

        return ShopItem(out_of_stock, name, cnt, discnt, cost)
