from flaskr.model import PartnershipParticipant
from flaskr.resources.partnership_subresource import (SubResourceItem,
                                                      SubResourceList)
from flaskr.schemas.family_tree import (PartnershipParticipantListSchema,
                                        PartnershipParticipantSchema)


class PartnersList(SubResourceList):
    model = PartnershipParticipant
    schema = PartnershipParticipantListSchema


class Partners(SubResourceItem):
    model = PartnershipParticipant
    schema = PartnershipParticipantSchema
