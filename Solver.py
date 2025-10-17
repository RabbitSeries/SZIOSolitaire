from __future__ import annotations
from enum import Enum
from heapq import heappop, heappush


class Location(Enum):
    Wild = 0
    Tray = 1
    cTray = 2
    BtnZZ = 3
    BtnFF = 4
    BtnBB = 5
    AutoCollect = 6


class State:
    @staticmethod
    def trayOrder(high: str, low: str):
        if not high[0].isdigit() or not low[0].isdigit():
            return False
        return high[1] != low[1] and ord(low[0]) == ord(high[0]) - 1

    @staticmethod
    def collectOrder(high: str, low: str):
        if not high[0].isdigit() or not low[0].isdigit():
            return False
        return high[1] == low[1] and ord(low[0]) == ord(high[0]) + 1

    # Meaning of move:
    # tuple[0]: Location where Card A is moved from
    # tuple[1]: Card A's postion in pile: tuple[int,int] or wild: int
    # tuple[2]: Loaction where Card A is moved to
    # tuple[3]: Card A's destination in pile(int)/wild(int)/button name(str)
    def __init__(self, trays: list[list[str]], cTrays: list[str | None], wildSlots: list[tuple[str, bool] | None], Yaoji: str | None,
                 moves: list[tuple[Location, tuple[int, int] | int | None, str, Location, tuple[int, int] | int | str]]):
        self.trays = trays
        self.cTrays = cTrays
        # Empty or tuple[card name, isLocked: true if this is a ZZ FF BB, false otherwise]
        self.wildSlots = wildSlots
        self.Yaoji = Yaoji
        self.moves = moves
        self.priority = self.calc_priority()

    def __lt__(self, rhs: State):
        return rhs.priority < rhs.priority

    def hash(self):
        return hash(";".join(sorted("".join(t) for t in self.trays)) + "|" + ";".join(sorted(wild[0] if wild else "None" for wild in self.wildSlots))
                    + "|"+";".join(sorted(c or "None" for c in self.cTrays)))

    def shadowcopy(self):
        return State([pile.copy() for pile in self.trays], self.cTrays.copy(), self.wildSlots.copy(), self.Yaoji, self.moves.copy())

    color = {"r": 0, "g": 1, "b": 2}

    def findCollect(self, card: str, RGB_Min: list[int]):
        # Rule: if current card can not connect any current wild slot | other cards in tray, collect it
        # That is card's must be min in RGB and not greater than other's RGB min
        # Rule2: if this card >= RGB_Min[color]
        # 1 2 None
        # then 2 can be collected
        if not card[0].isdigit():
            return None
        c = self.color[card[1]]
        face = int(card[0])
        # face == RGB_min[color], can be auto collected
        if face > RGB_Min[c]:
            return None
        # if this card is 2, auto collect
        if face != 2 and any(m for m in RGB_Min if m < face):
            return None
        return next(i for i, collect in enumerate(self.cTrays) if not collect or self.collectOrder(collect, card))

    def AutoCollectHelper(self):
        RGB_Min = [9]*3
        for tray in self.trays:
            for card in tray:
                if card[0].isdigit():
                    c = self.color[card[1]]
                    RGB_Min[c] = min(RGB_Min[c], int(card[0]))
        for wild in self.wildSlots:
            if wild and wild[0][0].isdigit():
                card = wild[0]
                c = self.color[card[1]]
                RGB_Min[c] = min(RGB_Min[c], int(card[0]))
        # Collect pile
        for i in range(len(self.trays)):
            if len(self.trays[i]) == 0:
                continue
            last_card = self.trays[i][-1]
            if last_card == "yy":
                # collect yaoji
                self.Yaoji = last_card
                self.trays[i] = self.trays[i][0:-1]
                return True
            else:
                collect = self.findCollect(last_card, RGB_Min)
                if collect is None:
                    continue
                self.cTrays[collect] = last_card
                self.trays[i] = self.trays[i][0:-1]
                return True
        # collect wild position
        for j, wild in enumerate(self.wildSlots):
            if wild is None or wild[1]:
                continue
            collect = self.findCollect(wild[0], RGB_Min)
            if collect is None:
                continue
            self.cTrays[collect] = wild[0]
            self.wildSlots[j] = None  # remove wild card
            return True
        return False

    def collectZZFFBB(self):
        # ===========================================================Collect ZZ FF BB, if collected no need to dfs, just move to next action
        for target, btn in zip(["zz", "ff", "bb"], [Location.BtnZZ, Location.BtnFF, Location.BtnBB]):
            found = self.findZFB(target)
            # If exposed is not 4
            # or there is no empty wild position can collect ZZ FF BB
            # or found positions does not include a target
            if len(found) != 4 or all(w is not None and w[0] != target for w in self.wildSlots):
                continue
            for j, location in found:
                if location == Location.Tray:
                    self.trays[j] = self.trays[j][0:-1]
                else:
                    # this exposed card is already in wildSlots, mark it empty anyways
                    self.wildSlots[j] = None
            # Then collecto is definitely not None
            collectTo = next(j for j in range(3) if self.wildSlots[j] is None)
            self.wildSlots[collectTo] = (target, True)
            self.moves.append((Location.Wild, (-1, -1), target, btn, target))
            return True
        return False

    # Exposed cards should be checked for auto collection
    def AutoCollect(self):
        def gen():
            while self.AutoCollectHelper():
                yield 0
        while True:
            collect = len(list(gen()))
            if collect > 0:
                self.moves.append((Location.AutoCollect, None,
                                   "",
                                   Location.AutoCollect, collect))
            if not self.collectZZFFBB() and collect == 0:
                break

    def moveToAnotherPile(self, pileOrWild: int | None, card: str, cutPointInPileOrWild: int | None):
        for j in range(len(self.trays)):
            if j == pileOrWild:
                continue
            # Move entire pile to empty pile is meaningless, unless moved card is wild card
            if cutPointInPileOrWild == 0 and len(self.trays[j]) == 0:
                continue
            # Move only to connect ordering or empty pile
            if len(self.trays[j]) > 0 and not self.trayOrder(self.trays[j][-1], card):
                continue
            # Move only to the first empty pile
            if len(self.trays[j]) == 0 and any(len(p) == 0 for p in self.trays[:j]):
                continue
            yield j

    def moveToWild(self) -> int | None:
        if any(len(pile) == 0 for pile in self.trays):
            return None
        return next((j for j, c in enumerate(self.wildSlots) if c is None), None)

    def findZFB(self, ZFB_Name: str):
        locations: list[tuple[int, Location]] = []
        # Count exposed cards for Hong Zhong or Fa Cai or Bai Ban
        for i, pile in enumerate(self.trays):
            if len(pile) > 0 and pile[-1] == ZFB_Name:
                locations.append((i, Location.Tray))
        for i, wild in enumerate(self.wildSlots):
            if wild is not None and wild[0] == ZFB_Name and not wild[1]:
                locations.append((i, Location.Wild))
        return locations

    def Solved(self):
        # remaining cards is 0 and wildslots are locked
        possible = all(len(pile) == 0 for pile in self.trays)
        if possible:
            print("Possible")
        return possible and all(w is not None and w[1] for w in self.wildSlots)

    def calc_priority(self):
        stackedCards = 0
        for pile in self.trays:
            if not pile:
                continue
            localStacked = 0
            for i in range(len(pile)-1, 0, -1):
                if State.trayOrder(pile[i-1], pile[i]):
                    localStacked += 1
                else:
                    break
            if localStacked == len(pile)-1 and pile[0][0] != '9':
                stackedCards += localStacked * 1.2
            else:
                stackedCards += localStacked * 1.1
        remaining = sum(len(t) for t in self.trays) + \
            sum(0 if w is None or w[1] else 1 for w in self.wildSlots)
        return remaining + len(self.moves)*0.1 - stackedCards

    def log(self):
        print(len(self.moves))
        print(self.trays)
        print(self.cTrays)
        print(self.wildSlots)
        # print(self.Yaoji)
        # print(self.found)
        print()


def Solve(init_s: State):
    init_s.AutoCollect()
    q: list[State] = [init_s]
    Cache: dict[int, int] = {init_s.hash(): len(init_s.moves)}

    def put_in(s: State):
        s.AutoCollect()
        hs = s.hash()
        cost = len(s.moves)
        if hs not in Cache or cost < Cache[hs]:
            Cache[hs] = cost
        heappush(q, s)

    def pop_out():
        return heappop(q)
    itreation = 0
    while itreation < 50000 and len(q) > 0:
        itreation += 1
        s = pop_out()
        if Cache[s.hash()] < len(s.moves):
            continue
        if s.Solved():
            return s.moves
        trays, wild, collected = s.trays, s.wildSlots, s.cTrays
        for i in range(len(trays)):
            if len(trays[i]) == 0:
                continue
            # ===========================================================Move cards in a pile to another
            for cutPoint in range(len(trays[i])):
                if any(not State.trayOrder(high, low) for high, low in zip(trays[i][cutPoint:], trays[i][cutPoint+1:])):
                    continue
                card_i = trays[i][cutPoint]
                truncated = trays[i][cutPoint:]
                for j in s.moveToAnotherPile(i, card_i, cutPoint):
                    ns = s.shadowcopy()
                    ns.trays[i] = trays[i][0:cutPoint]
                    ns.trays[j] += truncated
                    ns.moves += [(Location.Tray, (i, cutPoint),
                                  card_i,
                                  Location.Tray, (j, len(trays[j])))]
                    put_in(ns)
            # ===========================================================Move card in pile to collected
            c = trays[i][-1]
            for j, collect in enumerate(collected):
                if collect is None:
                    continue
                if State.collectOrder(collect, c):
                    ns = s.shadowcopy()
                    ns.cTrays[j] = c
                    ns.trays[i] = trays[i][0:-1]
                    ns.moves.append((Location.Tray, (i, len(ns.trays[i])),
                                     c,
                                     Location.cTray, j))
                    put_in(ns)
                    break
        for i, w in enumerate(wild):
            if w is None or w[1]:
                continue
            # ===========================================================Move a card from wild to pile
            for j in s.moveToAnotherPile(None, w[0], None):
                ns = s.shadowcopy()
                ns.wildSlots[i] = None
                ns.trays[j].append(w[0])
                ns.moves.append((Location.Wild, i,
                                 w[0],
                                Location.Tray, (j, len(trays[j]))))
                put_in(ns)
            # ===========================================================Move a card from wild to collected
            for j, collect in enumerate(collected):
                if collect is None:
                    continue
                if State.collectOrder(collect, w[0]):
                    ns = s.shadowcopy()
                    ns.cTrays[j] = w[0]
                    ns.wildSlots[i] = None
                    ns.moves.append((Location.Wild, i,
                                     w[0],
                                     Location.cTray, j))
                    put_in(ns)
                    break
        # A more strict rule here: only move the card the pile if no cards can be moved in piles
        # delta = len(q) - q_len
        # if delta != 0:
        #     continue
        # ===========================================================Move to wild card
        for i in range(len(trays)):
            if len(trays[i]) == 0:
                continue
            if (j := s.moveToWild()) is not None:
                ns = s.shadowcopy()
                ns.wildSlots[j] = (trays[i][-1], False)
                ns.moves.append((Location.Tray, (i, len(trays[i])-1),
                                 trays[i][-1],
                                Location.Wild, j))
                ns.trays[i] = trays[i][0:-1]
                put_in(ns)
    print(itreation)
    print(max(Cache.values()))
