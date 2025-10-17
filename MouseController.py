from typing import Literal
import win32api
import win32con
import time

from ScreenShot import Constants, Majiang


def move_mouse(from_pos: tuple[int, int], to_pos: tuple[int, int], steps: int = 200, delay: float = 0.001):
    """Smoothly move cursor from from_pos to to_pos"""
    x1, y1 = from_pos
    x2, y2 = to_pos
    for i in range(steps + 1):
        x = x1 + (x2 - x1) * i // steps
        y = y1 + (y2 - y1) * i // steps
        win32api.SetCursorPos((x, y))
        time.sleep(delay)


def leftClick(pos: tuple[int, int]):
    win32api.SetCursorPos(pos)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,  # type: ignore
                         0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,  # type: ignore
                         0, 0, 0, 0)
    time.sleep(0.1)


def Drag(from_pos: tuple[int, int], to_pos: tuple[int, int], button: Literal["left"] | Literal["right"] = "left"):
    """Drag mouse from A to B"""
    # Define button flags
    if button == "left":
        down_flag = win32con.MOUSEEVENTF_LEFTDOWN
        up_flag = win32con.MOUSEEVENTF_LEFTUP
    elif button == "right":
        down_flag = win32con.MOUSEEVENTF_RIGHTDOWN
        up_flag = win32con.MOUSEEVENTF_RIGHTUP
    else:
        raise ValueError("button must be 'left' or 'right'")
    # VOID mouse_event(
    #   [in] DWORD     dwFlags,
    #   [in] DWORD     dx,
    #   [in] DWORD     dy,
    #   [in] DWORD     dwData,
    #   [in] ULONG_PTR dwExtraInfo
    # );
    # Mouse down
    win32api.SetCursorPos(from_pos)
    time.sleep(0.1)
    win32api.mouse_event(down_flag, 0, 0, 0, 0)  # type: ignore
    time.sleep(0.1)
    # Move to target point smoothly
    move_mouse(from_pos, to_pos)
    # Mouse up
    win32api.SetCursorPos(to_pos)
    win32api.mouse_event(up_flag, 0, 0, 0, 0)  # type: ignore
    time.sleep(0.1)
    win32api.mouse_event(up_flag, 0, 0, 0, 0)  # type: ignore
    time.sleep(0.1)
    win32api.SetCursorPos((100, 100))


class MovePosition:
    default_scale = (1920, 1080)

    @staticmethod
    def normalize(pos: tuple[int, int] | tuple[float, float],  size: tuple[int, int], by: tuple[int, int] = default_scale):
        return (int(pos[0]/by[0]*size[0]), int(pos[1]/by[1]*size[1]))

    @staticmethod
    def normalizePercent(percent: tuple[float, float], size: tuple[int, int]):
        return Constants.cropCard(percent, size)

    @staticmethod
    def CollectPos(i: Literal[0, 1, 2] | int, size: tuple[int, int] = default_scale):
        center = Constants.cropCard((Constants.collect[0] + Constants.collectGap*i, Constants.collect[1]),
                                    size)
        return (int(center[0]+center[2])//2, int(center[1]+center[3])//2)

    @staticmethod
    def BtnPos(card: Literal[Majiang.hongzhong, Majiang.facai, Majiang.baiban], size: tuple[int, int] = default_scale):
        ZFB = Majiang.color(card)
        return MovePosition.normalize((889, 159 + (247-159)*ZFB), size)

    @staticmethod
    def WildPos(i: Literal[0, 1, 2] | int, size: tuple[int, int] = default_scale):
        center = Constants.cropCard((Constants.wild[0] + Constants.wildGap*i, Constants.wild[1]),
                                    size)
        return (int(center[0]+center[2])//2, int(center[1]+center[3])//2)

    @staticmethod
    def YaoJiPos(size: tuple[int, int] = default_scale):
        center = Constants.cropCard((965/1920, 124/1080), size)
        return (int(center[0]+center[2])//2, int(center[1]+center[3])//2)

    @staticmethod
    def TrayPos(Pile: Literal[0, 1, 2, 3, 4, 5, 6, 7] | int, Card: int, size: tuple[int, int] = default_scale):
        center = Constants.cropCard((Constants.piles[0]+Constants.columnGap*Pile,
                                     Constants.piles[1]+Constants.heightGap*Card),
                                    size)
        return (int(center[0]+center[2])//2, int(center[1]+center[3])//2)

    @staticmethod
    def newGamePos(size: tuple[int, int] = default_scale):
        return MovePosition.normalize((1509, 940), size)


if __name__ == "__main__":
    time.sleep(1)
    # print(win32api.GetCursorPos())
    # Drag(MovePosition.TrayPos(0, 4), MovePosition.TrayPos(1, 5))
    # time.sleep(1)
    # Drag(MovePosition.TrayPos(4, 3), MovePosition.WildPos(2))
    # Drag(MovePosition.TrayPos(2, 4), MovePosition.WildPos(0))
    Drag(MovePosition.TrayPos(4, 1), MovePosition.TrayPos(2, 4))
