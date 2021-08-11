from .speed_up import manufacture_speed_up
from .todo import collect_todo


def execute_base():
    collect_todo()
    manufacture_speed_up()
