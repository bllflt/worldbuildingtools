from wbcr.render.base import Base


class CharacterTableOfContents(Base):
  
    @classmethod
    def render_as_html(cls, data:dict) -> str:
        template = cls.env.get_template("toc.html")
        return template.render(data)
