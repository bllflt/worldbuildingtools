from flask_restful import Resource
from flaskr.model import db, Character as Model
from flaskr.schemas.character import CharacterSchema
from sqlalchemy import select
from flask import request


class CharacterList(Resource):

    def get(self):
        return CharacterSchema(many=True).dump(
            db.session.scalars(select(Model).order_by(Model.id)).all()
            )

    def post(self):
        datum = request.get_json()
        new_character = CharacterSchema().load(datum)
        db.session.add(new_character)
        db.session.commit()


class Character(Resource):
    pass
