from wbcr.characters.character import Character
from wbcr.render.base import Base


class CharacterOverview(Base):

    @classmethod
    def render_as_html(cls, character: Character) -> str:
        template = cls.env.get_template("overview.html")
        return template.render(character.get_overview_data())
