from typing import List
from PIL import Image

# Source: https://zhuanlan.zhihu.com/p/134088503


def difference(image: Image.Image) -> List[int]:
    """
    计算image的像素差值
    :param image: PIL.Image
    :return: 差值数组。0、1组成
    """
    # resize 大小越大, Hash值位数越多, 结果越精确
    resize_width = 9
    resize_height = 8
    # 1. resize to (9,8)
    smaller_image = image.resize((resize_width, resize_height))
    # 2. 灰度化 Grayscale
    grayscale_image = smaller_image.convert("L")
    # 3. 比较相邻像素
    pixels = list(grayscale_image.getdata())
    difference = []
    for row in range(resize_height):
        row_start_index = row * resize_width
        for col in range(resize_width - 1):
            left_pixel_index = row_start_index + col
            difference.append(pixels[left_pixel_index]
                              > pixels[left_pixel_index + 1])
    return difference


def dHash(image: Image.Image) -> str:
    """
    计算图片的dHash值
    :param image: PIL.Image
    :return: dHash值,string类型
    """
    diff = difference(image)
    # 转化为16进制(每个差值为一个bit,每8bit转为一个16进制)
    decimal_value = 0
    hash_string = ""
    for index, value in enumerate(diff):
        if value:  # value为0, 不用计算, 程序优化
            decimal_value += value * (2 ** (index % 8))
        if index % 8 == 7:
            # 每8位的结束
            # 不足2位以0填充。0xf=>0x0f
            hash_string += str(hex(decimal_value)[2:].rjust(2, "0"))
            decimal_value = 0
    return hash_string


def hamming_distance(dhash1: str, dhash2: str) -> int:
    """
    根据dHash值计算hamming distance
    :param dhash1: str
    :param dhash2: str
    :return: 汉明距离(int)
    """
    difference = (int(dhash1, 16)) ^ (int(dhash2, 16))
    return bin(difference).count("1")


if __name__ == '__main__':
    img1 = Image.open('1.jpg')
    img2 = Image.open('2.jpg')
    for img in [img1, img2]:
        valstr = dHash(img)
        val = int(valstr, 16)
    print(hamming_distance(dHash(img1), dHash(img2)))
