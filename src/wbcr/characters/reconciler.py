import re


class Reconciler:

    def __init__(self, image_root_dir, image_size=100):
        self._image_root_dir = image_root_dir
        self._image_size = image_size
        self._image_regex = ''.join(['!', r'\[', r'\[', self._image_root_dir,
                                    '/', r'[^ \[]', '*?.[.](?:png|jpg)',  r'\|',
                                     f'{self._image_size}', r'\]\]'])

    def insert_images(self, old_content: str, images: list) -> str:
        trimmed = re.sub(self._image_regex, '', old_content, 0, re.IGNORECASE)

        md = ''
        for image in images:
            md += f'![[{self._image_root_dir}/{image}|{self._image_size}]]'
        return f'{md}\n\n{trimmed}'

    def write_char_file(self, fname, images: list):
        with open(fname, "r+") as f:
            contents = f.read()
            contents = self.insert_images(contents, images)
            f.seek(0)
            f.write(contents)
            f.truncate()
