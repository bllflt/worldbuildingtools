#!/usr/bin/env python

import os
import re
import requests
import yaml
import json
from pathlib import Path

overview_data_path = Path('/Users/joel/Documents/Obsidian Vault/Characters')


with os.scandir(overview_data_path) as it:
    for file in it:
        name = file.name.replace('.md', '')
        md = Path(file).read_text()
        yml_text = re.search('(?:---)(.*?)(?:---)', md, 
                           re.DOTALL | re.MULTILINE)
        overview = yaml.safe_load(yml_text.group(1))
        if 'apperance' in overview:
            appearance = overview['apperance']
            del overview['apperance']
            overview['appearance'] = appearance
        if 'key-relationships' in overview:
            del overview['key-relationships']
        if 'key-relations' in overview:
            del overview['key-relations']
        if 'key_relationships' in overview:
            del overview['key_relationships']
        if 'gender' in overview:
            sex = overview['gender']
            del overview['gender']
            if sex == 'male':
                overview['sex'] = 1
            elif sex == 'female':
                overview['sex'] = 2
        if 'roleplaying' in overview:
            if overview['roleplaying'] is None:
                del overview['roleplaying']
            else:
                f = [];
                for role in overview['roleplaying']:
                   
                    if role is not None:
                        f.append(role)
                overview['roleplaying'] = f



        overview['name'] = name
       
        r = requests.post(
            'http://127.0.0.1:5000/api/v1/characters',
            headers={'content-type': 'application/json'},
            data=json.dumps(overview))
        if r.status_code != 200:
            print(name)
            print(r.status_code)
            print(r.text)
        

