from pathlib import Path
import os
import wbcr.config as config
from wbcr.characters.character import Character
import re
import yaml


class DaoOfCharacterOverViewData():
    root_path = Path(config.root_dir)
    overview_data_path = root_path.joinpath(config.character_dir)
    image_path = root_path.joinpath(config.image_dir)

    @classmethod
    def get_all_names(cls):
        rv = []
        with os.scandir(cls.overview_data_path) as it:
            for file in it:
                rv.append(file.name.replace(".md",  ""))
        return rv

    @classmethod
    def get_by_name(cls, name) -> Character:
        character = Character(name)
        md = Path(cls.overview_data_path.joinpath(f'{name}.md')).read_text()
        yml_text = re.search('(?:---)(.*?)(?:---)', md, re.DOTALL | re.MULTILINE)
        if yml_text is not None:
            overview = yaml.safe_load(yml_text.group(1))
            for k in overview:
                setattr(character, k, overview[k])

        images = []
        try:
            with os.scandir(cls.image_path / name) as it:
                for file in it:
                    if bool(re.search('(jpg|png)$', file.name, re.IGNORECASE)):
                        images.append(
                            Path(file.path).relative_to(
                                cls.root_path / 'characters',
                                walk_up=True))
        except:
            pass
        setattr(character, 'images', images)
        return character