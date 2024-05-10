#! /usr/bin/env python3

import os
import re

OBSIDIAN_ROOT = '~/Library/Mobile Documents/com~apple~CloudDocs/Documents/Obsidian Vault'
IMAGE_ROOT = '~/Library/Mobile Documents/com~apple~CloudDocs/Export'


def find_subdirs_with_images(root):
    pass

def decend_directory(dirname):
    pass

def check_filename(name):
    pass

def ignore_entry(name):

    rv = False
    match name:
        case '.DS_Store':
            rv = True
    return rv


def name_from_file(filename):
    pass

def ismarkdown(filename):
    return bool(re.search(r'*\.md$', filename))

def insert_images(filename, images):
    with open(filename, "r+") as f:
        contents = f.read()
        re.sub(r'!\[100\](file://*.png)', '', contents)
        new = ''
        for image in images:
            new += f'![100](file://{image})'
        
        # f.seek(0)
        # f.write(output)
        # f.truncate()
    
    

image_subdirs = find_subdirs_with_images(IMAGE_ROOT)

expanded = os.path.expanduser(OBSIDIAN_ROOT)
for entry in os.listdir(expanded):
    fullpath = f'{expanded}/{entry}'
    if ignore_entry(entry): next
    if os.path.isdir(fullpath):
        decend_directory(fullpath)
    elif ismarkdown(entry):
        char_name = name_from_file(entry)
        if char_name in image_subdirs:
            insert_images(fullpath, image_subdirs[char_name])