from flask_marshmallow import Marshmallow
from marshmallow.validate import Length

from flaskr.model import Character, Roleplaying, Image

ma = Marshmallow()


class RoleplayingSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Roleplaying
        load_instance = True


class ImageSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Image
        load_instance = True


class CharacterSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Character
        load_instance = True
    id = ma.auto_field(dump_only=True)
    name = ma.auto_field(validate=Length(min=1))
    roleplaying = ma.Pluck(RoleplayingSchema, 'characteristic', many=True)
    images = ma.Pluck(ImageSchema, 'uri', many=True)
