from functools import lru_cache
from typing import List, Optional, Union
from PIL import Image
from random import randint
import time
import os

from adb import AdbInterface, Key
from img import Box, img_match
from img.hash import dHash, hamming_distance

IMG_T = Union[str, Image.Image]


class Interface:
    def __init__(self, adb: AdbInterface, work_dir: str = '.') -> None:
        self.adb = adb
        self.work_dir = work_dir

    @lru_cache()
    def load_image(self, path: str) -> Image.Image:
        return Image.open(os.path.join(self.work_dir, path))

    def tap(self, box: Box) -> None:
        w, h = box.size
        x = box.x0 + randint(0, w)
        y = box.y0 + randint(0, h)
        self.adb.tap((x, y))

    def keyevent(self, key: Key) -> None:
        self.adb.keyevent(key)

    def text(self, text: str) -> None:
        self.adb.text(text)

    def screen(self, cached: bool = False, box: Box = None) -> Image.Image:
        while 1:
            img = self.adb.screencap(cached)
            if img is None:
                time.sleep(1)
            else:
                break
        return img.crop(box.xyxy) if box else img

    def img_crop(self, img: IMG_T, box: Box) -> Image.Image:
        if isinstance(img, str):
            img = self.load_image(img)
        return img.crop(box.xyxy)

    def img_match(self, pattern: IMG_T, img: IMG_T = None, thresh: float = 0.8) -> List[Box]:
        if img == None:
            img = self.screen()
        if isinstance(pattern, str):
            pattern = self.load_image(pattern)
        if isinstance(img, str):
            img = self.load_image(img)
        coords = img_match(pattern, img, thresh)
        return [Box.from_size(p, pattern.size) for p in coords]

    def img_tap(self, img: IMG_T, pending: float = None) -> bool:
        if isinstance(img, str):
            img = self.load_image(img)
        start = time.time()
        while 1:
            boxes = self.img_match(img)
            if boxes:
                break
            if pending is not None and time.time() - start > pending:
                return False
        self.tap(boxes[0])
        return True

    def img_diff(self, img1: IMG_T, img2: IMG_T) -> int:
        img1 = self.load_image(img1) if isinstance(img1, str) else img1
        img2 = self.load_image(img2) if isinstance(img2, str) else img2
        return hamming_distance(dHash(img1), dHash(img2))

    def wait_img(self, imgs: Union[List[str], str], pending: float = None) -> Optional[str]:
        if not isinstance(imgs, list):
            imgs = [imgs]
        start = time.time()
        while 1:
            for img in imgs:
                boxes = self.img_match(img)
                if boxes:
                    return img
            if pending is not None and time.time() - start > pending:
                break
        return None

    def wait_stable_img(self, pending: float = None, thresh: int = 3) -> bool:
        start = time.time()
        scr_prev = self.screen()
        while 1:
            time.sleep(2)
            scr_now = self.screen()
            if self.img_diff(scr_now, img2=scr_prev) <= thresh:
                break
            scr_prev = scr_now
            if pending is not None and time.time() - start > pending:
                return False
        return True
