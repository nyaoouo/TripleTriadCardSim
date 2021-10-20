import random
from typing import Optional, Tuple, List

"""
1	天选	出现什么规则完全交给命运女神来决定。
2	全明牌	互相公开手中所有的卡片进行游戏。
3	三明牌	互相随机公开手中三张卡片进行游戏。
4	同数	使出的卡片如果2边以上（含2边）的数值均与相邻的卡片数值相等，则会取得相邻卡片的控制权。
5	不胜不休	出现平局时会以场上双方各自控制的卡片重新开始对局。
6	加算	使出的卡片如果2边以上（含2边）的数值各自与相邻的卡片对应数值相加的和相等，则会取得相邻卡片的控制权。
7	随机	各自从手中所有卡片中随机抽出5张卡进行对局。
8	秩序	双方必须按照卡组中卡片的位置顺序使用卡片。
9	混乱	双方必须按照随机决定的顺序使用卡片。
10	逆转	逆转卡片的强度。
11	王牌杀手	A会被1所控制。逆转规则下1会被A所控制。
12	同类强化	带有类型的卡片会随场上设置的同一类型卡片的数量增多而变强。
13	同类弱化	带有类型的卡片会随场上设置的同一类型卡片的数量增多而变弱。
14	交换	双方随机从自己的卡组中抽出一张卡与对方交换。
15	选拔	以随机分配到的卡片组成卡组进行对战。
"""
random_rules = [2, 3, 4, 6, 8, 9, 10, 11, 12, 13, 14]
rules_gp = {2: 1, 3: 1, 8: 2, 9: 2, 12: 3, 13: 3}
cards: dict[int, 'Card'] = {}

NONE = 0
BLUE = 1
RED = -1
TOP = 1
BOTTOM = -1
LEFT = 2
RIGHT = -2

directions = [TOP, BOTTOM, LEFT, RIGHT]


class Card(object):
    def __init__(self, card_id: int, top: int, bottom: int, left: int, right: int, rarity: int, card_type: int):
        self.card_id = card_id
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right
        self.rarity = rarity
        self.type = card_type

    def get(self, direction: int):
        if direction == TOP:
            return self.top
        elif direction == BOTTOM:
            return self.bottom
        elif direction == LEFT:
            return self.left
        elif direction == RIGHT:
            return self.right


class Block(object):
    def __init__(self, game: 'GameState', block_id: int):
        self.block_id = block_id
        self.game = game
        self.card: Optional[Card] = None
        self.belongs_to = 0
        self.belongs_to_first = 0

    def copy(self, game=None):
        temp = self.__class__(game or self.game, self.block_id)
        temp.card = self.card
        temp.belongs_to = self.belongs_to
        temp.belongs_to_first = self.belongs_to_first
        return temp

    @property
    def has_top(self):
        return self.block_id > 2

    @property
    def has_bottom(self):
        return self.block_id < 6

    @property
    def has_left(self):
        return self.block_id % 3 > 0

    @property
    def has_right(self):
        return self.block_id % 3 < 2

    @property
    def top(self):
        if self.has_top:
            return self.game.blocks[self.block_id - 3]

    @property
    def bottom(self):
        if self.has_bottom:
            return self.game.blocks[self.block_id + 3]

    @property
    def left(self):
        if self.has_left:
            return self.game.blocks[self.block_id - 1]

    @property
    def right(self):
        if self.has_right:
            return self.game.blocks[self.block_id + 1]

    def get(self, direction: int):
        if direction == TOP:
            return self.top
        elif direction == BOTTOM:
            return self.bottom
        elif direction == LEFT:
            return self.left
        elif direction == RIGHT:
            return self.right

    def __bool__(self):
        return self.card is not None


class HandCard(object):
    def __init__(self, is_public: bool, card_id: int):
        self.is_public = is_public
        self.card_id = card_id
        self.card = cards.get(card_id)

    def __eq__(self, other):
        if other is None:
            return False
        elif isinstance(other, HandCard):
            return self.card_id == other.card_id
        elif isinstance(other, int):
            return self.card_id == other
        else:
            raise Exception(f"not supported type {other} {type(other)}")

    @property
    def is_unknown(self):
        return self.card is None

    def copy(self):
        return HandCard(self.is_public, self.card_id)


class GameState(object):
    def __init__(self,
                 first_player: int = None,
                 blue_cards: list[Tuple[bool, int]] = None,
                 red_cards: list[Tuple[bool, int]] = None,
                 rules: list[int] = None):
        self.round = 0
        self.blocks = [Block(self, i) for i in range(9)]
        self.current_player = BLUE if first_player is None else first_player
        self.blue_cards = [] if blue_cards is None else [HandCard(*card_id) for card_id in blue_cards]
        self.red_cards = [] if red_cards is None else [HandCard(*card_id) for card_id in red_cards]
        self.rules = rules
        self.type_cnt = dict()

    def score(self):
        return (sum(BLUE for card in self.blue_cards if card is not None) +
                sum(RED for card in self.red_cards if card is not None) +
                sum(block.belongs_to for block in self.blocks)) / 2

    def result(self):
        if sum(map(bool, self.blocks)) >= 9:
            return self.score()

    def copy(self):
        temp = self.__class__()
        temp.round = self.round
        temp.blocks = [block.copy(temp) for block in self.blocks]
        temp.blue_cards = [None if hand is None else hand.copy() for hand in self.blue_cards]
        temp.red_cards = [None if hand is None else hand.copy() for hand in self.red_cards]
        temp.rules = self.rules
        temp.type_cnt = self.type_cnt.copy()
        temp.current_player = self.current_player
        return temp

    def get_type_cnt(self, card_type):
        if not card_type:
            return 0
        return self.type_cnt.setdefault(card_type, 0)

    def get_strength(self, card: Card, direction: int):
        base = card.get(direction)
        if 12 in self.rules:
            return min(base + self.get_type_cnt(card.type), 10)  # 同类强化
        elif 13 in self.rules:
            return max(base - self.get_type_cnt(card.type), 1)  # 同类弱化
        else:
            return base

    def card_win(self, card1: Card, card2: Card, direction: int):
        card1_base = self.get_strength(card1, direction)
        card2_base = self.get_strength(card2, -direction)

        reverse = 10 in self.rules  # 逆转

        if 11 in self.rules:  # 王牌杀手
            if card1_base == 10 and card2_base == 1:
                return reverse
            elif card1_base == 1 and card2_base == 10:
                return not reverse
        if reverse:
            return card1_base < card2_base
        else:
            return card1_base > card2_base

    @property
    def current_cards(self) -> List[HandCard | None]:
        return self.blue_cards if self.is_blue else self.red_cards

    def place_card(self, block_id: int, hand_id: int, card_id: int):
        if card_id not in cards:
            raise Exception(f"Invalid card_id: {card_id}")
        if hand_id > 4 or hand_id < 0:
            raise Exception(f"Invalid hand_id: {hand_id}")
        if block_id > 8 or block_id < 0:
            raise Exception(f"Invalid block_id: {block_id}")
        if self.blocks[block_id].card is not None:
            raise Exception(f"Block-{block_id} is occupied by a card already")

        self.round += 1

        card = cards[card_id]
        block = self.blocks[block_id]
        self.blocks[block_id].card = card
        self.blocks[block_id].belongs_to = self.current_player
        self.blocks[block_id].belongs_to_first = self.current_player
        to_cal = {(card, block)}

        if 4 in self.rules:  # 同数
            pre_add = list()
            for direction in directions:
                target_block = block.get(direction)
                if (target_block and
                        self.get_strength(target_block.card, -direction) == self.get_strength(card, direction)):
                    pre_add.append((target_block.card, target_block))
            if len(pre_add) > 1:
                for target_card, target_block in pre_add:
                    if target_block.belongs_to != self.current_player:
                        target_block.belongs_to = self.current_player
                        to_cal.add((target_card, target_block))

        if 6 in self.rules:  # 加算
            pre_adds = dict()
            for direction in directions:
                target_block = block.get(direction)
                if target_block:
                    strength_sum = self.get_strength(target_block.card, -direction) + self.get_strength(card, direction)
                    pre_adds.setdefault(strength_sum, list()).append((target_block.card, target_block))
            for pre_add in pre_adds.values():
                if len(pre_add) > 1:
                    for target_card, target_block in pre_add:
                        if target_block.belongs_to != self.current_player:
                            target_block.belongs_to = self.current_player
                            to_cal.add((target_card, target_block))

        while to_cal:
            cal_card, cal_block = to_cal.pop()
            for direction in directions:
                target_block = cal_block.get(direction)
                if target_block and self.card_win(cal_card, target_block.card, direction):
                    target_block.belongs_to = self.current_player

        if card.type:
            self.type_cnt[card.type] = self.get_type_cnt(card.type) + 1
        self.current_cards[hand_id] = None
        self.current_player = -self.current_player

        return self

    @property
    def is_blue(self):
        return self.current_player == BLUE


def rand_confirm_rule(base_rule: list[int]):
    if 1 not in base_rule:
        return base_rule
    confirm_rule = []
    random_rule = 0
    exist_gp = set()
    for rule in base_rule:
        if rule == 1:
            random_rule += 1
        else:
            if rule in rules_gp:
                exist_gp.add(rules_gp[rule])
            confirm_rule.append(rule)
    for _ in range(random_rule):
        new = random.choice([r for r in random_rules if r not in confirm_rule and rules_gp.get(r) not in exist_gp])
        if new in rules_gp:
            exist_gp.add(rules_gp[new])
        confirm_rule.append(new)
    return confirm_rule


class Game(object):
    def __init__(self, base_rule: list[int]):
        self.base_rule = base_rule
        self.state: GameState | None = None
        self.blue_cards: list[int] | None = None
        self.red_cards: list[int] | None = None
        self.blue_seq: list[int] | None = None
        self.red_seq: list[int] | None = None

    def start_game(self, _red_cards: list[int], _blue_cards: list[int]):
        confirm_rule = rand_confirm_rule(self.base_rule)
        if 14 in confirm_rule:
            switch_idx = random.randint(0, 4)
            blue_cards = [_red_cards[i] if i == switch_idx else cid for i, cid in enumerate(_blue_cards)]
            red_cards = [_blue_cards[i] if i == switch_idx else cid for i, cid in enumerate(_red_cards)]
        else:
            blue_cards = _blue_cards
            red_cards = _red_cards
        if 8 in confirm_rule:
            red_seq = blue_seq = [i for i in range(5)]
        elif 9 in confirm_rule:
            blue_seq = [i for i in range(5)]
            random.shuffle(blue_seq)
            red_seq = [i for i in range(5)]
            random.shuffle(red_seq)
        else:
            red_seq = blue_seq = [5 for i in range(5)]
        if 2 in confirm_rule:
            game_red_cards = [(True, cid) for cid in red_cards]
            game_blue_cards = [(True, cid) for cid in blue_cards]
        elif 3 in confirm_rule:
            show_idx = random.choices([i for i in range(5)], k=3)
            game_red_cards = [(i in show_idx, cid) for i, cid in enumerate(red_cards)]
            game_blue_cards = [(i in show_idx, cid) for i, cid in enumerate(blue_cards)]
        else:
            game_red_cards = [(False, cid) for cid in red_cards]
            game_blue_cards = [(False, cid) for cid in blue_cards]
        first_player = random.choice([BLUE, RED])
        self.start_game_confirm(first_player, red_cards, blue_cards, red_seq, blue_seq, game_blue_cards, game_red_cards,
                                confirm_rule)

    def start_game_confirm(self,
                           first_player: int,
                           red_cards: list[int],
                           blue_cards: list[int],
                           red_seq: list[int],
                           blue_seq: list[int],
                           game_blue_cards: list[Tuple[bool, int]],
                           game_red_cards: list[Tuple[bool, int]],
                           confirm_rule: list[int],
                           ):
        self.red_seq = red_seq
        self.blue_seq = blue_seq
        self.red_cards = red_cards
        self.blue_cards = blue_cards
        self.state = GameState(first_player, game_blue_cards, game_red_cards, confirm_rule)

    @property
    def force_hand(self):
        return (self.red_seq if self.state.current_player == RED else self.blue_seq)[self.state.round // 2]
