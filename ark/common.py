from typing import Union
from adb import AdbInterface
from utils.interface import Interface
import logging

logging.basicConfig(format="[%(levelname)s] %(asctime)s %(name)s %(message)s")

try:
    adb = AdbInterface.get('emulator-5554')
except:
    adb = AdbInterface.get('127.0.0.1:5555')

ark_intf = Interface(adb, work_dir='ark/resource')


def get_logger(name: str, level: Union[int, str] = logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger
