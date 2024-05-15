from wbcr.characters.character import Character

from jinja2 import Environment, PackageLoader, select_autoescape


class CharacterOverview():

    @classmethod
    def render_as_html(cls, character: Character) -> str:

        env = Environment(
            loader=PackageLoader('wbcr', 'templates'),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True
        )
        template = env.get_template("overview.html")
        return template.render(character.get_overview_data())
