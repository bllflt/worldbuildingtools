from flask_marshmallow import Marshmallow

from flaskr.model import Character, Roleplaying

ma = Marshmallow()


class RoleplayingSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Roleplaying
        load_instance = True


class CharacterSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Character
        load_instance = True
    roleplaying = ma.Pluck(RoleplayingSchema, 'characteristic', many=True)

