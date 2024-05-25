from jinja2 import Environment, PackageLoader, select_autoescape


class Base():
    env = Environment(
            loader=PackageLoader('wbcr', 'templates'),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True
    )
