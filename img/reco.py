from typing import Any, Dict, List, Union
from cnstd import CnStd
from cnocr import CnOcr
from .common import Box, pil_to_cv
from PIL import Image

std = CnStd()
cn_ocr = CnOcr()

OCR_REPL = {'〇': '0', '①': '1', '②': '2', '③': '3', '④': '4',
            '⑤': '5', '⑥': '6', '⑦': '7', '⑧': '8', '⑨': '9',
            '=': '-', }


def recognize(img: Union[Image.Image, Any], crop: bool = False, repl: Dict[str, str] = {}) -> str:
    img = pil_to_cv(img) if isinstance(img, Image.Image) else img
    if crop:
        box_info_list = std.detect(img)
        for box_info in box_info_list:
            cropped_img = box_info['cropped_img']  # 检测出的文本框
            ocr_res = cn_ocr.ocr_for_single_line(cropped_img)
            result = ''.join(ocr_res)
            break
    else:
        result = ''.join(cn_ocr.ocr_for_single_line(img))

    repl = repl.copy()
    repl.update(OCR_REPL)

    for origin, replace in repl.items():
        result = result.replace(origin, replace)
    return result


def detect(img: Union[Image.Image]) -> List[Box]:
    img = pil_to_cv(img) if isinstance(img, Image.Image) else img
    box_info_list = std.detect(img)
    boxes = []
    for box_info in box_info_list:
        points = list(box_info['box'])
        boxes.append(Box(points[0], points[2]))
    return boxes


if __name__ == "__main__":
    for item in ['test/num.png', 'pcr/res/ok_white.png', 'pcr/res/fastpass_title.png', 'pcr/res/use_fp.png']:
        print(recognize(item))
