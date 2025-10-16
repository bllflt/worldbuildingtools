from flaskr.resources.crud_resource import GroupAPI, ItemAPI
from flaskr.model import Partnership as Model
from flaskr.schemas.family_tree import PartnershipSchema


class PartnershipList(GroupAPI):
    model = Model
    schema = PartnershipSchema


class Partnership(ItemAPI):
    model = Model
    schema = PartnershipSchema
