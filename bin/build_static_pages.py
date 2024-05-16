#!/usr/bin/env python

import re
from collections import defaultdict

from wbcr.characters.character import Character
from wbcr.dao import daoOfCharacterOverviewData
from wbcr.render.character_overview import CharacterOverview
from wbcr.render.toc import CharacterTableOfContents


def name_for_sorting(name: str) -> str:
    m = re.match(r'(Lord|Lady|Prince|Princess|Bishop|Queen)\s(.*)', name)
    if m is not None:
        name = m.group(1)[0]
    return name


names = daoOfCharacterOverviewData.get_all_names()
for name in names:
    character = Character(name)
    with open(name, 'w') as file:
        file.write(CharacterOverview.render_as_html(character))

by_first_letter = defaultdict([str])
for name in sorted(names, key=name_for_sorting):
    by_first_letter[name[0]].append(name)
with open('toc.html', 'w') as file:
    file.write(CharacterTableOfContents.render_as_html(by_first_letter))
