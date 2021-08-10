from .data import move_to_main_base
from .speed_up import manufacture_speed_up
from .todo import collect_todo


def execute_base():
    move_to_main_base()
    collect_todo()
    move_to_main_base()
    manufacture_speed_up()
