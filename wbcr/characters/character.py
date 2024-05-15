import re
from pathlib import Path
import os
import yaml


class Character():

    def __init__(self, name: str, **kwargs):
        self.name = name

    @classmethod
    def list_of_characer_nanes(cls):
        pass

    def load(self, root_dir: str, root_overview_dir: str):
        md = Path(f'{root_overview_dir}/{self.name}.md').read_text()
        yml = re.search('(?:---)(.*?)(?:---)', md, re.DOTALL | re.MULTILINE)
        if yml is not None:
            overview = yaml.safe_load(yml.group(1))
            for k in overview:
                setattr(self, k, overview[k])

        images = []
        pp = Path(f'{root_dir}')
        with os.scandir(pp / 'images' / self.name) as it:
            for file in it:
                if bool(re.search('(jpg|png)$', file.name, re.IGNORECASE)):
                    images.append(
                        Path(file.path).relative_to(pp / 'characters',
                                                    walk_up=True))
        setattr(self, 'images', images)

    def get_overview_data(self) -> dict:
        overview = {}
        for elm in ['images', 'name', 'apperance', 'roleplaying',
                    'background']:
            overview[elm] = getattr(self, elm)
        kr = []
        for rel_type in self.key_relationships:
            for rel in self.key_relationships[rel_type]:
                kr.append(rel)
        overview['kr_list'] = kr
        return overview

    def get_images(self):
        pass
