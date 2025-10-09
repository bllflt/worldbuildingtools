from flaskr.resources.crud_resource import GroupAPI, ItemAPI
from flaskr.model import Partnership
from flaskr.schemas.family_tree import PartnershipSchema


class PartnershipList(GroupAPI):
    model = Partnership
    schema = PartnershipSchema


class Partnership(ItemAPI):
    model = Partnership
    schema = PartnershipSchema
