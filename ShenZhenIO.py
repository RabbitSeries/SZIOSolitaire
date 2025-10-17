import time
from MouseController import Drag, MovePosition, leftClick
from Solver import Location, Solve, State
from ScreenShot import BestMatch, ExtractCollected, ExtractWild, ExtractYaoji, Majiang, MatchImages, ExtractTrays, capture_window_by_title, init, test


def main():
    # ============================== Templating
    init()
    # ============================== Test
    test()
    # ============================== DevTest
    # print(MatchImages(ExtractPiles(capture_window_by_title(), 0.1)))
    # ============================== Solve
    while True:
        screenshot = capture_window_by_title()
        size = screenshot.size
        trays = MatchImages(ExtractTrays(screenshot), 0.6)
        chance, name = BestMatch(ExtractYaoji(screenshot))
        Yaoji = name if chance >= 0.95 else None
        collected = [BestMatch(ExtractCollected(screenshot, i))
                     for i in range(3)]
        collected = [name if chance >
                     0.95 else None for chance, name in collected]
        wildSlot = [(name, name == "lc") if chance > 0.95 else None
                    for chance, name in [BestMatch(ExtractWild(screenshot, i)) for i in range(3)]]
        # if any(chance < 0.95 for chance, _ in collected):
        #     raise RuntimeError("Not recognized image")
        result = Solve(State(trays, collected, wildSlot, Yaoji, []))
        if result is None:
            print("None")
            time.sleep(2)
            leftClick(MovePosition.newGamePos())
            time.sleep(8)
            continue
        print(len(result))
        for fromType, fromLoc, cardName, toType, toLoc in result:
            if fromLoc is not None:
                print("Move", cardName, fromType,  f"{fromLoc[0]+1} at {fromLoc[1]+1}" if isinstance(fromLoc, tuple) else (fromLoc+1),
                      "to", toType, toLoc+1 if isinstance(toLoc, int) else toLoc if isinstance(toLoc, str) else tuple(map(lambda x: x+1, toLoc)))
            elif isinstance(toLoc, int):
                print("Auto collect")
                time.sleep(max(min(toLoc, 10), 2))
                continue
            time.sleep(1)
            if fromType == Location.Tray and isinstance(fromLoc, tuple):
                fromP2d = MovePosition.TrayPos(fromLoc[0], fromLoc[1], size)
                # ===========================================================Move cards in a pile to another
                if toType == Location.Tray and isinstance(toLoc, tuple):
                    Drag(fromP2d,
                         MovePosition.TrayPos(toLoc[0], toLoc[1], size))
                # ===========================================================Move to wild card
                elif toType == Location.Wild and isinstance(toLoc, int):
                    Drag(fromP2d,  MovePosition.WildPos(toLoc, size))
                # ===========================================================Move card in pile to collected
                elif toType == Location.cTray and isinstance(toLoc, int):
                    Drag(fromP2d,  MovePosition.CollectPos(toLoc, size))
                else:
                    raise RuntimeError("Move doen't satisfy rule")
            elif fromType == Location.Wild and isinstance(fromLoc, int):
                fromP2d = MovePosition.WildPos(fromLoc, size)
                # ===========================================================Move a card from wild to pile
                if toType == Location.Tray and isinstance(toLoc, tuple):
                    Drag(fromP2d,
                         MovePosition.TrayPos(toLoc[0], toLoc[1], size))
                elif toType == Location.cTray and isinstance(toLoc, int):
                    Drag(fromP2d, MovePosition.CollectPos(toLoc, size))
                else:
                    raise RuntimeError("Move doen't satisfy rule")
            elif fromType == Location.Wild and isinstance(fromLoc, tuple):
                # ===========================================================Move a card from wild to collected
                if toType == Location.BtnZZ:
                    leftClick(MovePosition.BtnPos(Majiang.hongzhong))
                elif toType == Location.BtnFF:
                    leftClick(MovePosition.BtnPos(Majiang.facai))
                elif toType == Location.BtnBB:
                    leftClick(MovePosition.BtnPos(Majiang.baiban))
                else:
                    raise RuntimeError("Move doen't satisfy rule")
                print(toType, "is collected by clicking", toLoc)
                time.sleep(1)
            else:
                raise RuntimeError("Move doen't satisfy rule")
            print()


if __name__ == "__main__":
    main()
