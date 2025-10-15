from flaskr.model import PartnershipParticipant
from flaskr.schemas.family_tree import PartnershipParticipantSchema
from flaskr.resources.partnership_subresource import (
    SubResourceList, SubResourceItem
)


class PartnersList(SubResourceList):
    model = PartnershipParticipant
    schema = PartnershipParticipantSchema


class Partners(SubResourceItem):
    model = PartnershipParticipant
    schema = PartnershipParticipantSchema
