from flask_restful import Resource
from flaskr.model import db, Character as Model
from flaskr.schemas.character import CharacterSchema
from marshmallow import ValidationError
from sqlalchemy import select, delete
from flask import request


class CharacterList(Resource):

    def get(self):
        return CharacterSchema(many=True).dump(
            db.session.scalars(select(Model).order_by(Model.id)).all()
            )

    def post(self):
        datum = request.get_json()
        try:
            new_character = CharacterSchema().load(datum)
        except ValidationError as err:
            return {'error': {
                "type": "validation",
                "message": err.normalized_messages()}
                }, 400

        db.session.add(new_character)
        db.session.commit()


class Character(Resource):
    def get(self, cid):
        character = db.session.scalar(select(Model).where(Model.id == cid))
        if character:
            return CharacterSchema().dump(character)
        else:
            return {'error': {
                'type': 'Not found'
            }}, 404

    def delete(self, cid):
        deleted = db.session.execute(delete(Model).where(
            Model.id == cid).returning(Model.id))
        found = deleted.one_or_none()
        deleted.close()
        db.session.commit()

        if found is None:
            return {'error': {
                'type': 'Not found'
            }}, 404
