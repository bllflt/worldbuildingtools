from flask import request
from flask_restful import Resource
from marshmallow import Schema, ValidationError
from sqlalchemy import delete, select
from sqlalchemy.orm import DeclarativeBase

from flaskr.model import db


class GroupAPI(Resource):
    model: DeclarativeBase = None  # to be set in subclass
    schema: Schema         = None  # to be set in subclass

    def get(self):
        return self.schema(many=True).dump(
            db.session.scalars(select(self.model).all())
        )

    def post(self):
        datum = request.get_json()
        try:
            new_item = self.schema().load(datum)
        except ValidationError as err:
            return {'error': {
                "type": "validation",
                "message": err.normalized_messages()}
                }, 400

        db.session.add(new_item)
        db.session.commit()
        return self.schema().dump(new_item), 201


class ItemAPI(Resource):
    def get(self, id):
        item = db.session.scalar(select(
            self.model).where(self.model.id == id))
        if item is not None:
            return self.schema().dump(item)
        return {'error': {'type': 'Not found'}}, 404

    def delete(self, item_id):
        deleted = db.session.execute(delete(self.model).where(
            self.model.id == item_id).returning(self.model.id))
        found = deleted.one_or_none()
        deleted.close()
        db.session.commit()
        if found is None:
            return {'error': {
                'type': 'Not found'
            }}, 404

    def put(self, item_id):
        item = db.session.scalar(select(
            self.model).where(self.model.id == item_id))
        if item is None:
            return {'error': {
                'type': 'Not found'
            }}, 404

        datum = request.get_json()
        try:
            self.schema().load(datum, instance=item)
        except ValidationError as err:
            return {'error': {
                "type": "validation",
                "message": err.normalized_messages()}
                }, 400

        db.session.commit()
