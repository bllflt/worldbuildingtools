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

        fields_key = request.args.get('fields')

        q = select(Model)
        if fields_key is not None:
            try:
                fields = set(fields_key.split(','))
                CharacterSchema(only=fields)
            except ValueError:
                return {'error': {
                    'type': 'Bad Request',
                    'message': f'Invalid fields: {fields_key}'
                }}, 400

            q = q.with_only_columns(*[getattr(Model, field)
                                      for field in fields])

        if sort_key is not None:
            q = q.order_by(text('name'))
        if filter_key is not None:
            q = q.where(
                Model.name.icontains(filter_key)
            )

        return CharacterSchema(many=True).dump(
           db.session.scalars(q).all() if fields_key is None
           else db.session.execute(q).all()
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
        return CharacterSchema().dump(new_character), 201


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
