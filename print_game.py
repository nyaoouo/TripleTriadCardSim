import ctypes

import define
from define import rule_name
from game import Game, BLUE, RED, HandCard

kernel32 = ctypes.WinDLL('kernel32')
hStdOut = kernel32.GetStdHandle(-11)
mode = ctypes.c_ulong()
kernel32.GetConsoleMode(hStdOut, ctypes.byref(mode))
mode.value |= 4
kernel32.SetConsoleMode(hStdOut, mode)


class BColors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


BLUE_COLOR = BColors.BLUE
RED_COLOR = BColors.RED


def fmt_game(game: Game):
    msg = '╔' + '═' * 7 * 3 + '╗'
    if game.state.current_player == BLUE:
        msg += ' ' * 4 + BLUE_COLOR + '┌blue' + '─' * (5 * 7 - 4) + '┐' + BColors.ENDC
    msg += '\n'
    force_hand = game.force_hand
    for i in range(3):
        for l in range(5):
            msg += '║'
            for j in range(3):
                block = game.state.blocks[i * 3 + j]
                if not block:
                    match l:
                        case 0:
                            msg += '┌─────┐'
                        case 4:
                            msg += '└─────┘'
                        case 2:
                            msg += f'│  {i * 3 + j}  │'
                        case _:
                            msg += '│     │'
                else:
                    msg += RED_COLOR if block.belongs_to == RED else BLUE_COLOR
                    flag = 'B' if game.state.current_player == BLUE else 'R'
                    match l:
                        case 0:
                            msg += f'┌{flag}────┐'
                        case 1:
                            msg += f'│  {block.card.top:X}  │'
                        case 2:
                            msg += f'│{block.card.left:X}   {block.card.right:X}│'
                        case 3:
                            msg += f'│  {block.card.bottom:X}  │'
                        case 4:
                            if block.card.type:
                                msg += f"└{block.card.card_id:03}─{block.card.type}┘"
                            else:
                                msg += f'└{block.card.card_id:03}──┘'
                    msg += BColors.ENDC
            msg += '║' + ' ' * 4
            if i == 0:
                d = game.state.blue_cards
                msg += BLUE_COLOR
                is_current = game.state.current_player == BLUE
            elif i == 2:
                d = game.state.red_cards
                msg += RED_COLOR
                is_current = game.state.current_player == RED
            else:
                match l:
                    case 0 if game.state.current_player == BLUE:
                        msg += BLUE_COLOR + '└' + '─' * 5 * 7 + '┘' + BColors.ENDC
                    case 1:
                        msg += f"round:{game.state.round}  current:{'blue' if game.state.current_player == BLUE else 'red'}  score:{game.state.score()}"
                    case 2:
                        msg += 'rule:' + ','.join(rule_name[rid] for rid in game.state.rules)
                    case 3:
                        msg += ' ; '.join(f"{define.type_name[t]}({t}):{c}" for t,c in game.state.type_cnt.items())
                    case 4 if game.state.current_player == RED:
                        msg += RED_COLOR + '┌red' + '─' * (5 * 7 - 3) + '┐' + BColors.ENDC
                msg += '\n'
                continue
            if is_current: msg += '│'
            hand: HandCard | None
            for j, hand in enumerate(d):
                if not hand:
                    msg += ' ' * 7
                else:
                    fill = ' ' if not is_current or force_hand > 4 or force_hand == j else '#'
                    if not hand.is_unknown and (hand.is_public or is_current):
                        match l:
                            case 0:
                                msg += f'┌──{j}──┐'
                            case 1:
                                msg += f'│{fill * 2}{hand.card.top:X}{fill * 2}│'
                            case 2:
                                msg += f'│{hand.card.left:X}{fill * 3}{hand.card.right:X}│'
                            case 3:
                                msg += f'│{fill * 2}{hand.card.bottom:X}{fill * 2}│'
                            case 4:
                                if hand.card.type:
                                    msg += f"└{hand.card.card_id:03}─{hand.card.type}┘"
                                else:
                                    msg += f'└{hand.card.card_id:03}──┘'
                    else:
                        match l:
                            case 0:
                                msg += f'┌──{j}──┐'
                            case 1 | 3:
                                msg += f'│{fill * 2}?{fill * 2}│'
                            case 2:
                                msg += f'│?{fill * 3}?│'
                            case 4:
                                msg += '└─────┘'
            if is_current:
                msg += '│'
            msg += BColors.ENDC + '\n'
    msg += '╚' + '═' * 7 * 3 + '╝'
    if game.state.current_player == RED:
        msg += ' ' * 4 + RED_COLOR + '└' + '─' * 5 * 7 + '┘' + BColors.ENDC
    return msg
