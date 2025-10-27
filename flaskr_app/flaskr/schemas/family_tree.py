from flask_marshmallow import Marshmallow

from flaskr.model import Partnership, PartnershipParticipant

ma = Marshmallow()


class PartnershipParticipantListSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PartnershipParticipant
    character_id = ma.auto_field(required=True)


class PartnershipParticipantSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PartnershipParticipant


class PartnershipSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Partnership
        load_instance = True
