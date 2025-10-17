from __future__ import annotations
from enum import Enum
# import math
from sys import prefix
import cv2 as cv
import numpy as np
import win32gui
import win32ui
import PIL.Image as PILImage
from PIL.Image import Image, frombuffer
import os
import win32con


def capture_window_by_title(window_title: str = "SHENZHEN I/O") -> Image:
    if not os.path.exists('screenshots'):
        os.makedirs('screenshots')

    try:
        # Find window by title
        hwnd = win32gui.FindWindow(None, window_title)
        if not hwnd:
            raise RuntimeError(f"Window '{window_title}' not found")

        # Get window dimensions
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width = right - left
        height = bottom - top

        # Create device context
        hwnd_dc = win32gui.GetWindowDC(hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()

        # Create bitmap
        bitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
        save_dc.SelectObject(bitmap)

        win32gui.BitBlt(
            save_dc.GetSafeHdc(), 0, 0, width, height, hwnd_dc, 0, 0, win32con.SRCCOPY)

        # Convert to PIL Image
        bmpstr = bitmap.GetBitmapBits(True)
        screenshot = frombuffer(
            'RGB',
            (width, height),
            bmpstr, 'raw', 'BGRX', 0, 1
        )

        # Cleanup
        win32gui.DeleteObject(bitmap.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwnd_dc)

        return screenshot

    except Exception as e:
        print(f"Error capturing window: {e}")
        raise e


class Constants:
    cardHeight = 0.023
    cardWidth = 0.014  # Keep only about a third width
    # cardWidth = 0.063 # Full width
    columnGap = 0.0792
    heightGap = 0.0288
    # Left, up, right, bottom
    piles = (0.2123, 0.366, 0.75, 0.845)

    # collect: 1164, 123
    # width: 1288, 122
    # height: 1160, 362
    # next: 1309, 124
    collect = (0.6080, 0.1205)
    collectGap = 0.079

    yaoji = (0.508, 0.1205)

    # yaoji: 965 124
    # height: (966, 365)

    wild = (0.2122, 0.1205)
    wildGap = 0.079

    @staticmethod
    def cropCard(leftUp: tuple[float, float], size: tuple[int, int]) -> tuple[float, float, float, float]:
        percent = (leftUp[0], leftUp[1], leftUp[0] +
                   Constants.cardWidth, leftUp[1] + Constants.cardHeight)
        return (percent[0]*size[0], percent[1]*size[1], percent[2]*size[0], percent[3]*size[1])


def Border(box: tuple[float, float, float, float], percent: float):
    width = box[2]-box[0]
    height = box[3]-box[1]
    return (box[0]+width*percent, box[1]+height*percent, box[2]-width*percent, box[3]-height*percent)


def ExtractTrayCardAt(screenshot: Image, column: int, card: int, border: float = 0):
    size = screenshot.size
    left = Constants.piles[0]+Constants.columnGap*column
    if left >= 1:
        return None
    top = Constants.piles[1] + Constants.heightGap * card
    if top >= 1:
        return None
    crop_box = Constants.cropCard((left, top), size)
    return screenshot.crop(Border(crop_box, border))


def ExtractTrays(screenshot: Image, border: float = 0, limit: int = 20):
    imageList: list[list[Image]] = []
    for column in range(8):
        imageList.append([])
        for i in range(limit):
            if (extract := ExtractTrayCardAt(screenshot, column, i, border)) is None:
                break
            imageList[column].append(extract)
            i = i+1
    return imageList


def ExtractYaoji(screenshot: Image, border: float = 0):
    size = screenshot.size
    crop_box = Constants.cropCard(Constants.yaoji, size)
    return screenshot.crop(Border(crop_box, border))


def ExtractCollected(screenshot: Image, card: int, border: float = 0):
    size = screenshot.size
    crop_box = Constants.cropCard((Constants.collect[0] + Constants.collectGap * card, Constants.collect[1]),
                                  size)
    return screenshot.crop(Border(crop_box, border))


def ExtractWild(screenshot: Image, card: int, border: float = 0):
    size = screenshot.size
    crop_box = Constants.cropCard((Constants.wild[0] + Constants.wildGap * card, Constants.wild[1]),
                                  size)
    return screenshot.crop(Border(crop_box, border))


class Majiang(Enum):
    @staticmethod
    def generate():
        for i, card_type in enumerate(["tiao", "bing", "wan"]):
            for j in range(9):
                print(f"{card_type}_{j+1} = {i*9+j}")
        print(f"facai = {3*9}")
        print(f"baiban = {3*9+1}")
        print(f"hongzhong = {3*9+2}")
        print(f"yaoji = {3*9+3}")

    @staticmethod
    def color(card: Majiang):
        return card.value // 9 if card.value < 3*9 else (card.value - 3*9)

    @staticmethod
    def face(card: Majiang):
        return card.value % 9 if card.value < 3*9 else None

    tiao_1 = 0
    tiao_2 = 1
    tiao_3 = 2
    tiao_4 = 3
    tiao_5 = 4
    tiao_6 = 5
    tiao_7 = 6
    tiao_8 = 7
    tiao_9 = 8
    bing_1 = 9
    bing_2 = 10
    bing_3 = 11
    bing_4 = 12
    bing_5 = 13
    bing_6 = 14
    bing_7 = 15
    bing_8 = 16
    bing_9 = 17
    wan_1 = 18
    wan_2 = 19
    wan_3 = 20
    wan_4 = 21
    wan_5 = 22
    wan_6 = 23
    wan_7 = 24
    wan_8 = 25
    wan_9 = 26
    hongzhong = 27
    facai = 28
    baiban = 29
    yaoji = 30


raw = [["7r", "1b", "ff", "4b", "6r"],
       ["3r", "7g", "6g", "4g", "bb"],
       ["5b", "8r", "7b", "zz", "9g"],
       ["9b", "1r", "1g", "ff", "bb"],
       ["ff", "4r", "zz", "9r", "ff"],
       ["bb", "5r", "8b", "yy", "bb"],
       ["6b", "2g", "3g", "2b", "5g"],
       ["2r", "zz", "zz", "3b", "8g"]]

prefix = "screenshots/"
template_paths = [*[[f"{prefix}card_{name}.png" for name in line]
                    for line in raw],
                  [f"{prefix}locked.png"]]


def BestMatch(image: Image):
    # image.save("tmp.png")
    cv_image = np.array(image.convert("RGB"))
    img_b, img_g, img_r = cv.split(cv_image)  # type: ignore
    results: list[tuple[float, str]] = []
    used: set[str] = set()
    for i, line in enumerate(template_paths):
        for j, path in enumerate(line):
            if i < len(raw):
                name = raw[i][j]
                if name in used:
                    continue
                used.add(name)
            else:
                name = "lc"
            template = cv.imread(path, cv.IMREAD_COLOR)
            tpl_b, tpl_g, tpl_r = cv.split(template)  # type: ignore
            # res = cv.matchTemplate(
            #     cv_image, template, cv.TM_CCOEFF_NORMED)  # type: ignore
            res_b = cv.matchTemplate(img_b, tpl_b, cv.TM_CCOEFF_NORMED)
            res_g = cv.matchTemplate(img_g, tpl_g, cv.TM_CCOEFF_NORMED)
            res_r = cv.matchTemplate(img_r, tpl_r, cv.TM_CCOEFF_NORMED)
            res = np.maximum(np.maximum(res_b, res_g), res_r)
            _, max_val, _, _ = cv.minMaxLoc(res)
            # _, max_val, _, _ = cv.minMaxLoc(res)
            results.append((max_val, name))
    # Sort templates by match score
    results.sort(key=lambda x: x[0], reverse=True)
    return results[0]


def MatchImages(images: list[list[Image]], allowance: float = 0.90):
    result: list[list[str]] = []
    # minChance = 1
    for pile in images:
        result.append([])
        for image in pile:
            chance, name = BestMatch(image)
            if chance < allowance:
                break
            # else:
                # minChance = min(minChance, chance)
            # print(math.floor(chance*100), name, end=" ")
            result[-1].append(name)
        # print()
    # print("Min chance", minChance)
    return result


def init():
    screenshot = PILImage.open("raw.png")
    extracted: set[str] = set()
    for i, column in enumerate(ExtractTrays(screenshot, -0.1, 5)):
        for j, image in enumerate(column):
            if raw[i][j] in extracted:
                continue
            extracted.add(raw[i][j])
            image.save(f"screenshots/card_{raw[i][j]}.png")
    debug = PILImage.open("debug.png")
    ExtractWild(debug, 0, -0.1).save("screenshots/locked.png")


def test():
    localRaw = PILImage.open("raw.png")
    images = ExtractTrays(localRaw)
    result = MatchImages(images)
    for i in range(len(result)):
        if len(result[i]) < len(raw[i]):
            print("Recognized count doesn't match")
        for j in range(len(result[i])):
            if result[i][j] != raw[i][j]:
                print(result[i][j], "expecting", raw[i][j])
    chance, _ = BestMatch(ExtractYaoji(localRaw))
    assert chance < 0.95

def debug():
    screenshot = PILImage.open("raw.png")
    ExtractYaoji(screenshot).save(f"yaoji.png")
    ExtractCollected(screenshot, 0).save("blank_collect_1.png")
    ExtractCollected(screenshot, 1).save("blank_collect_2.png")
    ExtractCollected(screenshot, 2).save("blank_collect_3.png")
    ExtractYaoji(screenshot).save("yaoji_blank.png")

    field = capture_window_by_title()
    ExtractYaoji(field).save("yaoji.png")
    for i in range(3):
        ExtractCollected(field, i).save(f"collect_{i}.png")
    for i in range(3):
        ExtractWild(field, i).save(f"wild_{i}.png")

    for i in range(5):
        if extract := ExtractTrayCardAt(field, 0, i):
            extract.save(f"Tray_0_{i}.png")

    for i in range(5):
        if extract := ExtractTrayCardAt(field, 6, i):
            extract.save(f"Tray_6_{i}.png")

    for i in range(5):
        if extract := ExtractTrayCardAt(field, 2, i):
            extract.save(f"Tray_2_{i}.png")


if __name__ == "__main__":
    init()
    test()
    debug()