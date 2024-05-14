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
         # simple case: add the images to empty body
         ('', ['ZiggyVanB/hook1.png', 'ZiggyVanB/hook2.png'], 
          '![[images/ZiggyVanB/hook1.png|100]]![[images/ZiggyVanB/hook2.png|100]]\n\n'),
         # preserve existing text
         ('existing text', ['green.png'],
          '![[images/green.png|100]]\n\nexisting text'),
         # remove old images
         ('![[images/ZiggyVanB/hook3.png|100]]![[images/ZiggyVanB/hook2.png|100]]',
          ['ZiggyVanB/hook1.png'], 
          '![[images/ZiggyVanB/hook1.png|100]]\n\n'),
         # remove old images: JPG - watch out
         ('![[images/ZiggyVanB/hook3.JPG|100]]![[images/ZiggyVanB/hook2.JPG|100]]',
          ['ZiggyVanB/hook1.png'], 
          '![[images/ZiggyVanB/hook1.png|100]]\n\n'),
         # preserve non image links
         ('![[images/ZiggyVanB/hook3.png|100]] existing text ![[something.png|100]]',
          ['A/B/C/splat.png'], 
          '![[images/A/B/C/splat.png|100]]\n\n existing text ![[something.png|100]]')
        ]
    )
    def test_insert_images(self, reconciler, old_content, images, expected_text):
        text = reconciler.insert_images(old_content, images)
        assert text == expected_text
