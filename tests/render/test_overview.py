import difflib
from pathlib import Path

from wbcr.characters.character import Character
from wbcr.render.character_overview import CharacterOverview


class TestRenderCharacterOverview:

    def test_render_as_html(self):

        test_data_dir = f'{Path(__file__).parent.parent}/vault'
        test_root_dir = f'{Path(__file__).parent.parent}'

        graurog = Character('Graurog')
        graurog.load(
            root_dir=test_root_dir,
            root_overview_dir=test_data_dir)
        html = CharacterOverview.render_as_html(graurog)

        diff = difflib.unified_diff(
            html,
            Path(f'{Path(__file__).parent}/Graurog.html').read_text(),
            fromfile='got', tofile='expected')
        assert list(diff) == []