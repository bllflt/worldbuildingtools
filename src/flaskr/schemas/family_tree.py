from flask_marshmallow import Marshmallow

from flaskr.model import Partnership, PartnershipParticipant, Offspring


ma = Marshmallow()


class PartnershipParticipantSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PartnershipParticipant
    character_id = ma.auto_field(required=True)


class OffspringSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Offspring
        load_instance = True
    character_id = ma.auto_field(required=True)


class PartnershipSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Partnership
        load_instance = True
