from flask_restful import Resource
from flaskr.model import db, Character, Partnership, PartnershipParticipant
from sqlalchemy import select


class CharacterPartnersResource(Resource):
    def get(self, cid):
        character = db.session.scalar(select(
            Character).where(Character.id == cid))
        if character is None:
            return {'error': {'type': 'Not found'}}, 404

        partnerships = db.session.scalars(
            select(Partnership).join(PartnershipParticipant).where(
                PartnershipParticipant.character_id == cid
            )
        ).all()

        result = []
        for partnership in partnerships:
            spouses = db.session.scalars(
                select(Character).join(PartnershipParticipant).where(
                    PartnershipParticipant.partnership_id == partnership.id,
                    PartnershipParticipant.character_id != cid
                )
            ).all()

            result.append({
                'id': partnership.id,
                'partnership_type': partnership.type,
                'start_date': partnership.start_date,
                'end_date': partnership.end_date,
                'is_primary': partnership.is_primary,
                'spouses': [{
                    'id': spouse.id,
                    'name': spouse.name,
                    'sex': spouse.sex
                } for spouse in spouses]
            })

        return result, 200
    

class CharacterChildrenResource(Resource):
    def get(self, cid):
        character = db.session.scalar(select(
            Character).where(Character.id == cid))
        if character is None:
            return {'error': {'type': 'Not found'}}, 404
        partnerships = db.session.scalars(
            select(Partnership).join(PartnershipParticipant).where(
                PartnershipParticipant.character_id == cid
                )).all()
        result = []
        for partnership in partnerships:
            spouses = db.session.scalars(
                select(
                    Character.id, Character.name, Character.sex,
                    ).join(PartnershipParticipant).where(
                    PartnershipParticipant.partnership_id == partnership.id,
                    PartnershipParticipant.character_id != cid
                )
            ).all()
            for spouse in spouses:
                children = []
                hadwith = []
                result.append({
                    'partnership_id': partnership.id,
                    'partnership_type': partnership.type,
                    'with': hadwith,
                    'children': children



                        # 'id': spouse.id,
                        # 'name': spouse.name,
                        # 'sex': spouse.sex,
                        # 'children': children
                        # }
                })
        return result, 200
