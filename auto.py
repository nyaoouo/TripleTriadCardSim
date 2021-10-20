import game
import solve
import define
import multiprocessing

define.init()
difficulty = 5000


def _test(mid, rule, deck1, deck2, blue_solver, red_solver, rtn_list):
    print("start", mid)
    _game = game.Game(rule)
    _game.start_game(deck1, deck2)

    while _game.state.result() is None:
        if _game.state.current_player == game.BLUE:
            h_id, b_id = blue_solver(_game, difficulty)
        else:
            h_id, b_id = red_solver(_game, difficulty)
        _game.state.place_card(b_id, h_id, _game.state.current_cards[h_id].card_id)
    rtn_list.append(_game.state.result())
    print("finish", mid)


def test(total, blue_solver, red_solver):
    pool = multiprocessing.Pool(processes=8)
    manager = multiprocessing.Manager()
    rtn_list = manager.list()
    counter = 0
    for i in range(total):
        rule = game.rand_confirm_rule([1, 1, 1])
        deck1 = solve.get_deck(rule)
        deck2 = solve.get_deck(rule)
        counter += 1
        pool.apply_async(_test, args=(counter, rule, deck1, deck2, blue_solver, red_solver, rtn_list))
        counter += 1
        pool.apply_async(_test, args=(counter, rule, deck2, deck1, blue_solver, red_solver, rtn_list))
    pool.close()
    pool.join()
    blue_win = 0
    blue_score = 0
    red_win = 0
    red_score = 0
    draw = 0
    for res in rtn_list:
        if res > 0:
            blue_win += 1
            blue_score += res
            red_score -= res
        elif res < 0:
            red_win += 1
            blue_score += res
            red_score -= res
        else:
            draw += 1
    print(f"blue: {blue_win},{blue_score}\tred: {red_win},{red_score}\tdraw:{draw}")


if __name__ == '__main__':
    test(100, solve.solve_min_max, solve.solve_avg)
