from flask import request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy import delete

from flaskr.model import Character, Partnership, PartnershipParticipant, db
from flaskr.schemas.family_tree import PartnershipParticipantSchema


class PartnersList(Resource):
    def get(self, pid):
        if db.session.query(Partnership).filter_by(id=pid).count() == 0:
            return {'error': {'type': 'Not found'}}, 404
        return PartnershipParticipantSchema(many=True).dump(
          db.session.query(PartnershipParticipant).filter_by(
              partnership_id=pid).all()
        )

    def post(self, pid):
        datum = request.get_json()
        result = []
        for spouse in datum:
            try:
                new_spouse = PartnershipParticipantSchema().load(spouse)
                new_spouse['partnership_id'] = pid
            except ValidationError as err:
                return {'error': {
                    "type": "validation",
                    "message": err.normalized_messages()}
                    }, 400
            result.append(PartnershipParticipant(**new_spouse))
        db.session.add_all(result)
        db.session.commit()
        return PartnershipParticipantSchema().dump(result), 201


class Partners(Resource):
    def get(self, pid, cid):
        if db.session.query(Partnership).filter_by(id=pid).count() == 0:
            return {'error': {'type': 'Partnership Not found'}}, 404
        if db.session.query(Character).filter_by(id=cid).count() == 0:
            return {'error': {'type': 'Character Not found'}}, 404
        return PartnershipParticipantSchema(many=True).dump(
          db.session.query(PartnershipParticipant).filter_by(
              partnership_id=pid,
              character_id=cid
              ).all()
        )

    def put(self, pid, cid):
        old = db.session.scalar(PartnershipParticipant).filter_by(
            partnership_id=pid,
            character_id=cid
        )
        datum = request.get_json()

        if old:
            try:
                PartnershipParticipantSchema().load(datum, instance=old)
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

    def delete(self, pid, cid):
        deleted = db.session.execute(delete(PartnershipParticipant).where(
            PartnershipParticipant.character_id == cid,
            PartnershipParticipant.partnership_id == pid).returning(
                PartnershipParticipant.character_id))
        found = deleted.one_or_none()
        if found is None:
            return {'error': {
                'type': 'Not found'
            }}, 404
        else:
            deleted.close()
        db.session.commit()
