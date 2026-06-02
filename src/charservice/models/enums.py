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

    @classmethod
    def opposite_role(cls, role: "RoleCode") -> "RoleCode":
        return {
            cls.PROTEGE: cls.MENTOR,
            cls.MENTOR: cls.PROTEGE,
            cls.LIEGE: cls.RETAINER,
            cls.RETAINER: cls.LIEGE,
            cls.PATRON: cls.CLIENT,
            cls.EMPLOYER: cls.EMPLOYEE,
            cls.EMPLOYEE: cls.EMPLOYER,
            cls.MASTER: cls.SLAVE,
            cls.SLAVE: cls.MASTER,
            cls.COMMANDER: cls.SUBBORDIATE,
            cls.SUBBORDIATE: cls.COMMANDER,
            cls.GUARDIAN: cls.WARD,
            cls.WARD: cls.GUARDIAN,
            cls.FRIEND: cls.FRIEND,
            cls.MATE: cls.MATE,
            cls.BETROTHED: cls.BETROTHED,
            cls.CONCUBINE: cls.MATE,
            cls.PARAMOUR: cls.PARAMOUR,
        }[role]


class Ptype(IntEnum):
    LIAISON = 1
    FACTION = 2
