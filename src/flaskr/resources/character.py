from flask_restful import Resource
from flaskr.model import db, Character as Model
from flaskr.schemas.character import CharacterSchema
from marshmallow import ValidationError
from sqlalchemy import select, delete, text
from flask import request


class CharacterList(Resource):

    def get(self):

        sort_key = request.args.get('sort')

        filter_key = request.args.get('name')

        q = select(Model)
        if sort_key is not None:
            q = q.order_by(text('name'))
        if filter_key is not None:
            q = q.where(
                Model.name.icontains(filter_key)
            )

        return CharacterSchema(many=True).dump(
            db.session.scalars(q).all()
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

    def put(self, cid):
        old = db.session.scalar(select(Model).where(Model.id == cid))
        datum = request.get_json()

        # XXX why - should id be in the payload? and why is it so fagile if
        # it is
        if 'id' in datum:
            del datum['id']

        if old:
            db.session.connection().exec_driver_sql(
                "DELETE FROM roleplaying WHERE character_id = ?",
                (old.id,))
            try:
                CharacterSchema().load(datum, instance=old)
            except ValidationError as err:
                return {'error': {
                    "type": "validation",
                    "message": err.normalized_messages()}
                    }, 400
            db.session.commit()
        else:
            return {'error': {
                'type': 'Not found'
                }}, 404
