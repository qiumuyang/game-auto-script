from typing import Any, Tuple
import cv2
import numpy as np
from PIL import Image, ImageFile
from functools import lru_cache

COORDINATE_T = Tuple[int, int]

# image file is truncated
ImageFile.LOAD_TRUNCATED_IMAGES = True


class Box:
    Left = 1
    Right = 2
    Up = 4
    Down = 8

    def __init__(self, p0: COORDINATE_T, p1: COORDINATE_T) -> None:
        x = sorted([p0[0], p1[0]])
        y = sorted([p0[1], p1[1]])
        self.p0 = (x[0], y[0])
        self.p1 = (x[1], y[1])

    @staticmethod
    def from_size(p: COORDINATE_T, size: Tuple[int, int]):
        p1 = tuple(p[i] + size[i] for i in [0, 1])
        return Box(p, p1)

    def next(self, direc: int):
        incr = [0, 0]
        if direc & self.Left:
            incr[0] -= self.w
        if direc & self.Right:
            incr[0] += self.w
        if direc & self.Up:
            incr[1] -= self.h
        if direc & self.Down:
            incr[1] += self.h
        next_p0 = self.x0 + incr[0], self.y0 + incr[1]
        return Box.from_size(next_p0, self.size)

    def contains(self, box) -> bool:
        return self.x0 <= box.x0 and self.x1 >= box.x1 and self.y0 <= box.y0 and self.y1 >= box.y1

    def __repr__(self) -> str:
        return str(self.xywh)

    @property
    def w(self) -> int:
        return self.x1 - self.x0

    @w.setter
    def w(self, value: int) -> None:
        self.x1 = self.x0 + value

    @property
    def h(self) -> int:
        return self.y1 - self.y0

    @h.setter
    def h(self, value: int) -> None:
        self.y1 = self.y0 + value

    @property
    def x0(self) -> int:
        return self.p0[0]

    @x0.setter
    def x0(self, value: int) -> None:
        self.p0 = (value, self.p0[1])

    @property
    def x1(self) -> int:
        return self.p1[0]

    @x1.setter
    def x1(self, value: int) -> None:
        self.p1 = (value, self.p1[1])

    @property
    def y0(self) -> int:
        return self.p0[1]

    @y0.setter
    def y0(self, value: int) -> None:
        self.p0 = (self.p0[0], value)

    @property
    def y1(self) -> int:
        return self.p1[1]

    @y1.setter
    def y1(self, value: int) -> None:
        self.p0 = (self.p1[0], value)

    @property
    def valid(self) -> bool:
        return all(self.p0[i] < self.p1[i] for i in [0, 1])

    @property
    def xyxy(self) -> Tuple[int, int, int, int]:
        ''' left, upper, right, lower '''
        return self.x0, self.y0, self.x1, self.y1

    @property
    def p1p2(self) -> Tuple[COORDINATE_T, COORDINATE_T]:
        ''' left-upper, right-lower '''
        return self.p0, self.p1

    @property
    def xywh(self) -> Tuple[COORDINATE_T, Tuple[int, int]]:
        ''' left-upper, size '''
        return self.p0, (self.w, self.h)

    @property
    def size(self) -> Tuple[int, int]:
        return self.w, self.h


def pil_to_cv(img: Image.Image) -> Any:
    assert(isinstance(img, Image.Image))
    return cv2.cvtColor(np.asarray(img.convert('RGB')), cv2.COLOR_RGB2BGR)


def pil_to_cvgray(img: Image.Image) -> Any:
    assert(isinstance(img, Image.Image))
    return cv2.cvtColor(np.asarray(img.convert('RGB')), cv2.COLOR_RGB2GRAY)


def cv_to_pil(img: Any) -> Image.Image:
    return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))


@lru_cache(maxsize=None)
def load_image(path: str) -> Image.Image:
    return Image.open(path)


if __name__ == '__main__':
    b1 = Box((1, 1), (5, 8))
    b2 = Box.from_size((1, 1), (4, 7))
    for property in ['x0', 'x1', 'y0', 'y1', 'w', 'h', 'p0', 'p1']:
        v1 = getattr(b1, property)
        v2 = getattr(b2, property)
        assert(v1 == v2)
    b1.x0 = 100
    b2.x0 = 100
    for property in ['x0', 'x1', 'y0', 'y1', 'w', 'h', 'p0', 'p1']:
        v1 = getattr(b1, property)
        v2 = getattr(b2, property)
        assert(v1 == v2)
    print(b1.valid)
