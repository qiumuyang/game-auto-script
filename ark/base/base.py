from ark.base.shift import do_normal_shift, do_manufacture_shift
from .speed_up import manufacture_speed_up
from .todo import collect_todo


def execute_base():
    collect_todo()
    manufacture_speed_up()
    do_manufacture_shift()
    do_normal_shift()
