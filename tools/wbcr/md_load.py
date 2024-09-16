#!/usr/bin/env python

import os
import re
import requests
import yaml
import json
from pathlib import Path

overview_data_path = Path('/Users/joel/Documents/wbcr/character md')

with os.scandir(overview_data_path) as it:
    for file in it:
        name = file.name.replace('.md', '')
        md = Path(file).read_text()
        yml_text = re.search('(?:---)(.*?)(?:---)', md,
                             re.DOTALL | re.MULTILINE)
        overview = yaml.safe_load(yml_text.group(1))
        overview['name'] = name
        overview['sex'] = {
            'na': 9, 'male': 1, 'female': 2, 'unknown': 0}[overview['sex']]
        if overview['roleplaying'] is None:
            overview['roleplaying'] = []

        r = requests.post(
            'http://127.0.0.1:5000/api/v1/characters',
            headers={'content-type': 'application/json'},
            data=json.dumps(overview))
        if r.status_code != 200:
            print(name)
            print(r.status_code)
            print(r.text)
        

