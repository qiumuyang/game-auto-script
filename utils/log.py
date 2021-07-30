import logging
from typing import Union


FMT = "[%(levelname)s] %(asctime)s %(name)s %(message)s"
DATEFMT = "%Y-%m-%d %H:%M:%S"

formatter = logging.Formatter(fmt=FMT, datefmt=DATEFMT)


def get_logger(name: str, level: Union[int, str] = logging.DEBUG):
    logger = logging.Logger(name)
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
