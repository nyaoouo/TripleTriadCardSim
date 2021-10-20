import define
import game
import print_game
import solve

define.init()

if __name__=='__main__':
    try:
        _difficulty = int(input("input difficulty 1(easiest) - 5(hardest)<<"))
    except ValueError:
        _difficulty = 3

    match _difficulty:
        case 1:
            difficulty = 10000
        case 2:
            difficulty = 30000
        case 4:
            difficulty = 100000
        case 5:
            difficulty = 200000
        case n if n > 1000:
            difficulty = n
        case _:
            difficulty = 50000

    rules = [int(i) for i in input("input rule id(s) separate by ',' (default:1,1) <<").split(',') if i] or [1, 1]
    _game = game.Game(rules)
    user_deck = [int(i) for i in input("input card deck separate by ',' (empty for auto) <<").split(',') if i]
    if len(user_deck) < 5: user_deck = solve.get_deck(rules)
    bot_deck = solve.get_deck(rules)
    print(f"rules:", ','.join(define.rule_name[i] for i in rules))
    print(f"user deck:", ','.join(define.card_name[i] for i in user_deck))
    # print(f"bot deck:",','.join(define.card_name[i] for i in bot_deck))
    _game.start_game(bot_deck, user_deck)


    def ask_user():
        h_id, b_id = [int(i) for i in input("input hand id, block id separate by ' '<<").split(' ') if i]
        return h_id, b_id


    while _game.state.result() is None:
        print(print_game.fmt_game(_game))
        print('*' * 60)
        if _game.state.current_player == game.BLUE:
            # h_id, b_id = ask_user()
            h_id, b_id = solve.solve_avg_multiprocess(_game, difficulty)
        else:
            h_id, b_id = solve.solve_avg_multiprocess(_game, difficulty)
        _game.state.place_card(b_id, h_id, _game.state.current_cards[h_id].card_id)

    print(print_game.fmt_game(_game))
    print("result:", _game.state.result())
