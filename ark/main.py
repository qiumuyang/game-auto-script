from .battle.battle import execute_single_level
from .shop.shop import execute_purchase
from .start.start import start_game
from .nav.navigate import move_to_last_level, move_to_shop


def simple_routine():
    start_game()
    if move_to_last_level():
        execute_single_level()
    move_to_shop()
    execute_purchase()
