from csv import DictReader
from pathlib import Path

import game

lang = 'chs'
definitions = Path('definitions')

card_name = dict()
rule_name = dict()
type_name = dict()

def init():
    main_fields = ['cid', 'top', 'bottom', 'left', 'right', 'rarity', 'type']
    with open(definitions / 'card_main.csv', encoding='utf8') as fi:
        for row in DictReader(fi, lineterminator='\n', fieldnames=main_fields):
            game.cards[int(row['cid'])] = game.Card(
                int(row['cid']),
                int(row['top']),
                int(row['bottom']),
                int(row['left']),
                int(row['right']),
                int(row['rarity']),
                int(row['type'])
            )


    # card_desc = dict()
    with open(definitions / f'card_{lang}.csv', encoding='utf8') as fi:
        for row in DictReader(fi, lineterminator='\n', fieldnames=['cid', 'name', 'desc']):
            card_name[int(row['cid'])] = row['name']
            # card_desc[int(row['cid'])] = row['desc']

    with open(definitions / f'rule_{lang}.csv', encoding='utf8') as fi:
        for row in DictReader(fi, lineterminator='\n', fieldnames=['id', 'name']):
            rule_name[int(row['id'])] = row['name']

    with open(definitions / f'type_{lang}.csv', encoding='utf8') as fi:
        for row in DictReader(fi, lineterminator='\n', fieldnames=['id', 'name']):
            type_name[int(row['id'])] = row['name']
