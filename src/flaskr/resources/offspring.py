from flaskr.resources.crud_resource import GroupAPI, ItemAPI
from flaskr.model import Offspring
from flaskr.schemas.family_tree import OffspringSchema


class OffspringList(GroupAPI):
    model = Offspring
    schema = OffspringSchema


class Offspring(ItemAPI):
    model = Offspring
    schema = OffspringSchema
