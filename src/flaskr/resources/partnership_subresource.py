from flask import request
from marshmallow import ValidationError
from sqlalchemy import delete, select

from flaskr.model import Character, Partnership, db
from flaskr.resources.crud_resource import GroupAPI, ItemAPI


class SubResourceList(GroupAPI):
    def get(self, pid):
        if db.session.query(Partnership).filter_by(id=pid).count() == 0:
            return {'error': {'type': 'Not found'}}, 404
        return self.schema(many=True).dump(
          db.session.query(self.model).filter_by(
              partnership_id=pid).all()
        )

    def post(self, pid):
        datum = request.get_json()
        result = []
        for item in datum:
            try:
                new_sr = self.schema().load(item)
                new_sr['partnership_id'] = pid
            except ValidationError as err:
                return {'error': {
                    "type": "validation",
                    "message": err.normalized_messages()}
                    }, 400
            result.append(self.model(**new_sr))
        db.session.add_all(result)
        db.session.commit()
        return self.schema().dump(result), 201


class SubResourceItem(ItemAPI):
    def get(self, pid, cid):
        if db.session.query(Partnership).filter_by(id=pid).count() == 0:
            return {'error': {'type': 'Partnership Not found'}}, 404
        if db.session.query(Character).filter_by(id=cid).count() == 0:
            return {'error': {'type': 'Character Not found'}}, 404
        return self.schema(many=True).dump(
          db.session.query(self.model).filter_by(
              partnership_id=pid,
              character_id=cid
              ).all()
        )

    def put(self, pid, cid):
        if db.session.query(Partnership).filter_by(id=pid).count() == 0:
            return {'error': {'type': 'Partnership Not found'}}, 404
        if db.session.query(Character).filter_by(id=cid).count() == 0:
            return {'error': {'type': 'Character Not found'}}, 404
        old = db.session.execute(select(self.model).where(
            self.model.partnership_id == pid,
            self.model.character_id == cid
        )).scalar()
        if old:
            return None, 409
        new_item = self.model(
            partnership_id=pid,
            character_id=cid
        )
        db.session.add(new_item)
        db.session.commit()

    def delete(self, pid, cid):
        deleted = db.session.execute(delete(self.model).where(
            self.model.character_id == cid,
            self.model.partnership_id == pid).returning(
                self.model.character_id))
        found = deleted.one_or_none()
        if found is None:
            return {'error': {
                'type': 'Not found'
            }}, 404
        deleted.close()
        db.session.commit()
