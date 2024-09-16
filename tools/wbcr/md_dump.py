#!/usr/bin/env python

import os
from pathlib import Path

import requests

overview_data_path = Path('/Users/joel/Documents/wbcr/character md')

r = requests.get('http://127.0.0.1:5000/api/v1/characters')
os.chdir(overview_data_path)
for item in r.json():
    del item['id']
    name = item['name']
    with open(f'{item['name'].rstrip()}.md', 'w') as file:
        file.write('---\n')
        file.write('appearance: |-\n')
        file.write(f'  {item['appearance']}\n')
        file.write('\n')
        file.write('roleplaying:\n')
        for rp in item['roleplaying']:
            file.write(f'  - {rp}\n')
        file.write('\n')
        file.write('background: |-\n')
        file.write(f'  {item['background']}\n')
        file.write('\n')
        file.write('sex: {}\n'.format(
            {9: 'na', 1: 'male', 2: 'female', 0: 'unknown'}[
                item['sex']
            ]))
        file.write('---\n')
