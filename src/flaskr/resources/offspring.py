from flaskr.resources.partnership_subresource import (SubResourceList,
                                                      SubResourceItem)
from flaskr.model import Offspring as Model
from flaskr.schemas.family_tree import OffspringSchema


class OffspringList(SubResourceList):
    model = Model
    schema = OffspringSchema


class Offspring(SubResourceItem):
    model = Model
    schema = OffspringSchema
