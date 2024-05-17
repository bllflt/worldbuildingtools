import difflib
from pathlib import Path

from wbcr.dao.daoOfCharacterOverviewData import DaoOfCharacterOverViewData
from wbcr.render.character_overview import CharacterOverview


class TestRenderCharacterOverview:

    def test_render_as_html(self):
        graurog = DaoOfCharacterOverViewData.get_by_name('Graurog')
        html = CharacterOverview.render_as_html(graurog)

        diff = difflib.unified_diff(
            html,
            Path(f'{Path(__file__).parent}/Graurog.html').read_text(),
            fromfile='got', tofile='expected')
        assert list(diff) == []
