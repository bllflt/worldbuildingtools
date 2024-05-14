#! /usr/bin/env python3

import os
import re
import shutil

OBSIDIAN_ROOT = '~/Library/Mobile Documents/com~apple~CloudDocs/Documents/Obsidian Vault'
IMAGE_DIR = 'external_images'
CHARACTER_DIR = 'Characters'
CHARACTER_TEMPLATE = 'Templates/Character Sheet.md'

character_data_from_image = {}
os.chdir(os.path.expanduser(OBSIDIAN_ROOT))
with os.scandir('external_images') as it:
    for entry in it:
        if (entry.name in ['.DS_Store', 'Characters not yet in the saga',
                           'Uncatagorized']):
            continue
        if entry.is_file(): 
            continue
        with os.scandir(entry.path) as image_it:
            images = []
            for sub_entry in image_it:
                if bool(re.search('(jpg|png)$', sub_entry.name, re.IGNORECASE)):
                    images.append(sub_entry.path)
            character_data_from_image[entry.name] = images

character_data_from_obsidian = {}
with os.scandir('Characters') as it:
    for entry in it:
        name = re.sub('.md$', '', entry.name)
        if name in character_data_from_image:
            print(f'{name}: ')
            for img in character_data_from_image[name]:
                print(f"\t {img}")
            del character_data_from_image[name]
        else:
            print(f'{name} is missing picture(s)')
for key in character_data_from_image:
    
    print(f'{key} is missing a note')             
