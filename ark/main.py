from ark.base.todo import collect_todo
from .battle.battle import execute_single_level
from .shop.shop import execute_purchase
from .start.start import start_game
from .nav.navigate import move_to_base, move_to_last_level, move_to_shop
from .nav.request import collect_request_reward
from .nav.friend import collect_friend_credit


def simple_routine():
    start_game()

    # 重复前一次作战
    if move_to_last_level():
        execute_single_level()

    # 访问好友基建
    collect_friend_credit()

    # 信用商店
    move_to_shop()
    execute_purchase()

    # 基建
    move_to_base()
    collect_todo()

    # 任务奖励
    collect_request_reward()
