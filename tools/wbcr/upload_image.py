#!/usr/bin/env python

import os
import re
import shutil
from pathlib import Path
from uuid import uuid4

from sqlalchemy import create_engine, text

img_dir = Path(
    '/Users/joel/Library/Mobile Documents/com~apple~CloudDocs/Covenant of Shifting Lights/World Building/images')
prod_dir = Path('/Users/joel/Documents/wbcr/images')

engine = create_engine("sqlite://///Users/joel/Documents/wbcr/wbcr.sqllite")

with engine.connect() as con:
    rs = con.execute(text('select id, name from character'))
    for row in rs:
        id = row[0]
        name = row[1]
        try:
            with os.scandir(img_dir / name) as it:
                for file in it:
                    m = re.match(r'(?:.*)\.(jpg|png|webp)$', file.name,
                                     re.IGNORECASE)
                    if bool(m):
                        uuid = uuid4().hex + '.' + m.group(1)
                        print(uuid)
                        shutil.copyfile(file, prod_dir / uuid)
                        con.execute(
                             text(
                                f'insert into images (character_id, uri) values ({id},"{uuid}")'
                            ))
        except (Exception) as e:
            print(e)
            pass
    con.commit()
