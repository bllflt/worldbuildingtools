#!/usr/bin/env python

from wbcr.dao.daoOfCharacterOverviewData import DaoOfCharacterOverViewData
import wbcr.config as config
from pathlib import Path
import os
import shutil
import re

have_data = set(DaoOfCharacterOverViewData.get_all_names())

image_root_dir = Path(config.root_dir).joinpath(config.image_dir)
with os.scandir(image_root_dir) as it:
    for item in it:
        if not item.is_dir:
            continue
        if item.name in (
            'Characters not yet in the saga',
            'Uncatagorized',
            '.DS_Store'
            ):
            continue
        if item.name not in have_data:
            shutil.copy('template.md', f'{item.name}.md')
            print(f"{item.name} was  missing overview")
        else:
            with os.scandir(image_root_dir.joinpath(item.name)) as subitr:
                for file in subitr:
                    if bool(re.match(r'(?:.*)\.(?:jpg|png)$', file.name,
                            re.IGNORECASE)):
                        have_data.remove(item.name)
                        break
for name in have_data:
    print(f"{name} has no images")
