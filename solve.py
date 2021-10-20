import traceback
from random import sample, shuffle, choice

import game
import multiprocessing
import time


def time_check(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        ans = func(*args, **kwargs)
        print(f"{func.__name__} took {time.perf_counter() - start:.2f}s")
        return ans

    return wrapper


def available_action(state: game.GameState, force_hand: int = 5, allow_try=20000):
    ans = list()
    empty_block = [i for i in range(9) if state.blocks[i].card is None]
    for hand_id, hand_card in enumerate(state.current_cards):
        if hand_card is None or 5 > force_hand != hand_id: continue
        for b_id in empty_block:
            ans.append((b_id, hand_id, hand_card.card.card_id))
    if len(ans) > allow_try:
        ans = sample(ans, allow_try)
    if not ans:
        raise Exception('no action')
    return ans, (allow_try - len(ans)) // len(ans) + 1


def _solve_min_max(_game: game.Game, state: game.GameState, allow_try=20000):
    res = state.result()
    if res is not None: return res, -1, -1
    actions, each_allow = available_action(state, (_game.blue_seq if state.is_blue else _game.red_seq)[state.round // 2], allow_try)
    d = ((_solve_min_max(_game, state.copy().place_card(*a), each_allow)[0], a[1], a[0]) for a in actions)
    return (max if state.is_blue else min)(d, key=lambda x: x[0])


def solve_min_max(_game: game.Game, allow_try=20000):
    score, h_id, b_id = _solve_min_max(_game, _game.state, allow_try)
    return h_id, b_id


def _solve_avg(_game: game.Game, state: game.GameState, allow_try=20000):
    res = state.result()
    if res is not None: return res
    actions, each_allow = available_action(state, (_game.blue_seq if state.is_blue else _game.red_seq)[state.round // 2], allow_try)
    return sum(_solve_avg(_game, state.copy().place_card(*a), each_allow) for a in actions) / len(actions)

@time_check
def solve_avg(_game: game.Game, allow_try=20000):
    actions, each_allow = available_action(_game.state, _game.force_hand, allow_try)
    b_id, h_id, c_id = (max if _game.state.is_blue else min)(actions, key=lambda a: _solve_avg(_game, _game.state.copy().place_card(*a), each_allow))
    return h_id, b_id


def _solve_avg_multiprocess(key, rtn_dict, _game: game.Game, state: game.GameState, allow_try=20000):
    try:
        rtn_dict[key] = _solve_avg(_game, state, allow_try)
    except:
        print(traceback.format_exc())

@time_check
def solve_avg_multiprocess(_game: game.Game, allow_try=20000):
    actions, each_allow = available_action(_game.state, _game.force_hand, allow_try)
    manager = multiprocessing.Manager()
    rtn_dict = manager.dict()
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    for block_id, hand_id, card_id in actions:
        state = _game.state.copy().place_card(block_id, hand_id, card_id)
        pool.apply_async(_solve_avg_multiprocess, args=((hand_id, block_id), rtn_dict, _game, state, each_allow))
    pool.close()
    pool.join()
    return (max if _game.state.is_blue else min)(rtn_dict, key=rtn_dict.get)


def try_choose(cards, limit=True):
    choose = list()
    cnt5 = 0
    cnt4 = 0
    if cards[5]:
        cnt5 = 1
        choose = [choice(cards[5])]
    if cards[4]:
        cnt4 = min(1 if limit else (2 - len(choose)), len(cards[4]))
        choose += sample(cards[4], cnt4)
    cnto = 0
    for i in range(3, 0, -1):
        if (cnto >= 3) if limit else (len(choose) >= 5): break
        l = min((3 - cnto) if limit else (5 - len(choose)), len(cards[i]))
        cnto += l
        choose += sample(cards[i], l)
    return choose, cnt5, cnt4


types = {i: list() for i in range(5)}


def get_deck(rules):
    cards = {i: list() for i in range(1, 6)}
    cardsT = {t: {i: list() for i in range(1, 6)} for t in types}
    same = 12 in rules
    dif = 13 in rules
    rev = 10 in rules
    need_type = same and not rev or dif and rev
    need_n_type = dif and not rev or same and rev
    for card in game.cards.values():
        cards[card.rarity].append(card.card_id)
        cardsT[card.type][card.rarity].append(card.card_id)
    choose, cnt5, cnt4 = list(), 0, 0
    if need_n_type:
        choose, cnt5, cnt4 = try_choose(cardsT[0])
    elif need_type:
        order = [t for t in types if t]
        shuffle(order)
        choose, cnt5, cnt4 = max([try_choose(cardsT[t]) for t in order], key=lambda x: len(x[0]))
    if len(choose) < 5:
        if cards[5] and not cnt5:
            cnt5 = 1
            choose += [choice(cards[5])]
        if len(choose) < 5:
            c4 = [card for card in cards[4] if card not in choose]
            if c4 and cnt4 + cnt5 < 2: choose += sample(c4, min(2 - cnt4 - cnt5, len(c4)))
        for i in range(3, 0, -1):
            if len(choose) >= 5: break
            c = [card for card in cards[i] if card not in choose]
            choose += sample(c, min(5 - len(choose), len(c)))
    shuffle(choose)
    return choose
