from flaskr.resources.partnership_subresource import SubResourceList, SubResourceItem
from flaskr.model import Offspring
from flaskr.schemas.family_tree import OffspringSchema


class OffspringList(SubResourceList):
    model = Offspring
    schema = OffspringSchema


class Offspring(SubResourceItem):
    model = Offspring
    schema = OffspringSchema
