from dataclasses import dataclass

from charservice.models.enums import RoleCode


@dataclass(slots=True)
class Member:
    character_id: str 
    role_code: RoleCode

@dataclass(slots=True)
class Association:
    name: str

