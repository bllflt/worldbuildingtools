import difflib
import shutil
import tempfile
from pathlib import Path

import pytest

from wbcr.characters.reconciler import Reconciler

ROOT = 'images'
WIDTH = 100


@pytest.fixture()
def reconciler():
    return Reconciler(ROOT, WIDTH)


class TestReconciler:

    @pytest.mark.parametrize(
        "old_content, images, expected_text",
        [
         # simple case: add the images
         ('', ['images/ZiggyVanB/hook1.png', 'images/ZiggyVanB/hook2.png'], 
          '![[images/ZiggyVanB/hook1.png|100]]![[images/ZiggyVanB/hook2.png|100]]\n\n'),
         # preserve existing text
         ('existing text', ['images/green.png'],
          '![[images/green.png|100]]\n\nexisting text'),
         # remove old images
         ('![[images/ZiggyVanB/hook3.png|100]]![[images/ZiggyVanB/hook2.png|100]]',
          ['images/ZiggyVanB/hook1.png'], 
          '![[images/ZiggyVanB/hook1.png|100]]\n\n'),
         # remove old images: JPG - watch out
         ('![[images/ZiggyVanB/hook3.JPG|100]]![[images/ZiggyVanB/hook2.JPG|100]]',
          ['images/ZiggyVanB/hook1.png'], 
          '![[images/ZiggyVanB/hook1.png|100]]\n\n'),
         # preserve non image links
         ('![[images/ZiggyVanB/hook3.png|100]] existing text ![[something.png|100]]',
          ['images/A/B/C/splat.png'], 
          '![[images/A/B/C/splat.png|100]]\n\n existing text ![[something.png|100]]')
        ]
    )
    def test_insert_images(self, reconciler, old_content, images, expected_text):
        text = reconciler.insert_images(old_content, images)
        assert text == expected_text

    def test_rewrite_char_file(self, reconciler):

        test_data_dir = f'{Path(__file__).parent}/vault'

        with open(f'{test_data_dir}/Graurog.md', 'r') as ep:
            expected_text = ep.readlines()

        with tempfile.NamedTemporaryFile(mode='r+') as fp:
            shutil.copy(f'{test_data_dir}/GraurogMissingImages.md', fp.name)
            reconciler.write_char_file(fp.name, [
                'external_images/Graurog/IMG_0914.JPG',
                'external_images/Graurog/medium_close_up___ogre_1_1___nun_s_habit__tusks_-_baddream__fastnegativev2__2156574829.png'
            ])
            got_text = fp.readlines()
            diff = difflib.unified_diff(got_text, expected_text,
                                        fromfile='got', tofile='expected')
            assert list(diff) == []
