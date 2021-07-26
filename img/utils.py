from functools import reduce
from typing import List, Tuple, Union
from PIL import Image, ImageDraw
import numpy as np
import cv2
from .common import cv_to_pil, pil_to_cvgray, Box, COORDINATE_T


def img_crop(img: Image.Image, box: Box) -> Image.Image:
    assert(box.valid)
    return img.crop(box.xyxy)


def img_match(pattern: Image.Image, img: Image.Image, threshold: float = 0.8) -> List[COORDINATE_T]:
    pattern = pil_to_cvgray(pattern)
    img = pil_to_cvgray(img)
    result = cv2.matchTemplate(img, pattern, cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= threshold)

    point_list = []
    for tup in zip(*loc[::-1]):
        point = tup[0], tup[1]
        if all(abs(p[0] - point[0]) + abs(p[1] - point[1]) > 10
               for p in point_list):
            point_list.append(point)
    return point_list


def img_mark(img: Image.Image, boxes: Union[Box, List[Box]], color: Tuple[int, int, int] = (0, 0, 255), width: int = 1) -> Image.Image:
    img = img.copy()
    draw = ImageDraw.ImageDraw(img)
    if isinstance(boxes, Box):
        boxes = [boxes]
    for box in boxes:
        draw.rectangle(box.p1p2, fill=None, outline=color, width=width)
    return img


def binarization(img: Image.Image, thresh: int = 127) -> Image.Image:
    img_gray = pil_to_cvgray(img)
    val, img = cv2.threshold(img_gray, thresh, 255, cv2.THRESH_BINARY)
    return cv_to_pil(img)


def img_cmp(src: Image.Image, dst: Image.Image) -> float:
    def phash(img: Image.Image) -> int:
        img = img.resize((8, 8), Image.ANTIALIAS).convert('L')
        avg = reduce(lambda x, y: x + y, img.getdata()) / 64.
        hash_value = reduce(lambda x, y: x | (y[1] << y[0]), enumerate(
            map(lambda i: 0 if i < avg else 1, img.getdata())), 0)
        return hash_value

    src_hash = phash(src)
    dst_hash = phash(dst)
    distance = bin(src_hash ^ dst_hash).count('1')
    # starts with '0b'
    bit_count = len(bin(max(src_hash, dst_hash))) - 2
    similary = 1 - distance / bit_count
    return similary
