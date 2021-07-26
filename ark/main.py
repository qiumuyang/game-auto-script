import logging
logging.basicConfig(format="[%(levelname)s] %(asctime)s %(name)s %(message)s")

from .battle.battle import execute_single_level
from .shop.shop import execute_purchase
