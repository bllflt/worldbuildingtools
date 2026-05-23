from enum import IntEnum, StrEnum


# ISO/IEC 5218
class Sex(IntEnum):
    UNKNOWN = 0
    MALE = 1
    FEMALE = 2
    NA = 9


class RoleCode(StrEnum):
    MATE = "MATE"
    CHILD = "CHILD"
    MEMBER = "MEMBER"
    CONCUBINE = "CONCUBINE"
    BETROTHED = "BETROTHED"
    PARAMOUR = "PARAMOUR"
    GUARDIAN = "GUARDIAN"
    WARD = "WARD"
    MENTOR = "MENTOR"
    PROTEGE = "PROTEGE"
    LIEGE = "LIEGE"
    RETAINER = "RETAINER"
    PATRON = "PATRON"
    CLIENT = "CLIENT"
    EMPLOYER = "EMPLOYER"
    EMPLOYEE = "EMPLOYEE"
    MASTER = "MASTER"
    SLAVE = "SLAVE"
    COMMANDER = "COMMANDER"
    SUBBORDIATE = "SUBBORDINATE"
    FRIEND = "FRIEND"


class Ptype(IntEnum):
    LIAISON = 1
    FACTION = 2
