#!/usr/bin/env python

import re
from collections import defaultdict

from wbcr.dao.daoOfCharacterOverviewData import DaoOfCharacterOverViewData
from wbcr.render.character_overview import CharacterOverview
from wbcr.render.toc import CharacterTableOfContents


def name_for_sorting(name: str) -> str:
    royal_title_pattern = '|'.join([
        'Duke',
        'Duchess',
        'Lord',
        'Lady',
        'Prince(?: Consort)?',
        'Princess(?: Consort)?',
        'Bishop',
        'Queen',
        'King',
        'Sir'
    ])
    m = re.match(r'(?:'
                 + royal_title_pattern
                 + ')'
                 + r'\s(.*)', name)
    if m is not None:
        name = m.group(1)
    return name


names = DaoOfCharacterOverViewData.get_all_names()
for name in names:
    character = DaoOfCharacterOverViewData.get_by_name(name)
    with open(f'{name}.html', 'w') as file:
        file.write(CharacterOverview.render_as_html(character))

names_for_sorting = {}
for name in names:
    names_for_sorting[name_for_sorting(name)] = name

by_first_letter = defaultdict(list)
for sort_name in sorted(names_for_sorting.keys()):
    by_first_letter[sort_name[0]].append(names_for_sorting[sort_name])
with open('toc.html', 'w') as file:
    file.write(CharacterTableOfContents.render_as_html(by_first_letter))
