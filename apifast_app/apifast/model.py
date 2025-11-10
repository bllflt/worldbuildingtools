import enum
from typing import Annotated, Literal

from pydantic import BaseModel, computed_field
from pydantic import Field as PydanticField
from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


# ISO/IEC 5218
class Sex(enum.IntEnum):
    UNKNOWN = 0
    MALE = 1
    FEMALE = 2
    NA = 9


class Role(enum.IntEnum):
    MATE = 1
    CHILD = 2
    MEMBER = 3


class Ptype(enum.IntEnum):
    LIAISON = 1
    FACTION = 2


class CharacterBase(BaseModel):
    name: str
    background: str | None = None
    appearance: str | None = None
    sex: Sex = Field(default=Sex.NA, description="0=unknown, 1=male, 2=female, 9=na")


class Character(SQLModel, CharacterBase, table=True):
    sex: int | None = Field(
        default=Sex.NA, sa_column_args=[CheckConstraint("sex IN (0, 1, 2, 9)")]
    )
    id: int | None = Field(default=None, primary_key=True)

    roleplaying_attributes: list["Roleplaying"] = Relationship(
        back_populates="character_link",
        passive_deletes=True,
        cascade_delete=True,
    )
    image_attributes: list["Image"] = Relationship(
        back_populates="character_link",
        passive_deletes=True,
        cascade_delete=False,
    )


class CharacterRead(CharacterBase):
    id: int

    model_config = {
        "from_attributes": True,
    }

    roleplaying_attributes: list["Roleplaying"] = PydanticField(exclude=True)
    image_attributes: list["Image"] = PydanticField(exclude=True)

    @computed_field(return_type=list[str])
    @property
    def roleplaying(self) -> list[str]:
        return [rp.characteristic for rp in self.roleplaying_attributes]

    @computed_field(return_type=list[str])
    @property
    def images(self) -> list[str]:
        return [i.uri for i in self.image_attributes]


class CharacterWrite(CharacterBase):
    roleplaying: list[str] = []
    images: list[str] = []


class Roleplaying(SQLModel, table=True):
    __tablename__ = "roleplaying"

    id: int | None = Field(default=None, primary_key=True)
    characteristic: str | None = Field(
        default=None,
        min_length=1,
        sa_column_args=[CheckConstraint("length(trim(characteristic)) > 0")],
    )
    character_id: int | None = Field(
        default=None, foreign_key="character.id", ondelete="CASCADE"
    )
    character_link: "Character" = Relationship(back_populates="roleplaying_attributes")


class Image(SQLModel, table=True):
    __tablename__ = "images"

    id: int | None = Field(default=None, primary_key=True)
    character_id: int | None = Field(
        default=None,
        foreign_key="character.id",
        ondelete="SET NULL",
    )
    uri: str | None = Field(
        default=None,
        min_length=1,
        sa_column_args=[CheckConstraint("length(trim(uri)) > 0")],
    )
    character_link: "Character" = Relationship(back_populates="image_attributes")


class FactionMember(BaseModel):
    id: int
    role: Role
    name: str | None = None
    sex: Sex | None = None


class SocialNetwork(BaseModel):
    id: int
    participants: list[FactionMember] = []
    start_date: str | None = None
    end_date: str | None = None


class Liaison(SocialNetwork):
    type: Literal[Ptype.LIAISON] = Field(default=Ptype.LIAISON, description="A liaison")
    is_primary: bool = Field(default=False, description="Is this a primary liaison")
    legitimate: bool = Field(default=False, description="Is this a legitimate liaison")


class Faction(SocialNetwork):
    type: Literal[Ptype.FACTION] = Field(default=Ptype.FACTION, description="A faction")
    name: str | None = None


SocialConnection = Annotated[Liaison | Faction, PydanticField(discriminator="type")]


class PartnershipBase(BaseModel):
    type: Ptype
    start_date: str | None = Field(default=None)
    end_date: str | None = Field(default=None)
    is_primary: bool | None = Field(default=False)
    legitimate: bool | None = Field(default=False)
    name: str | None = Field(default=None)


class Partnership(SQLModel, PartnershipBase, table=True):
    __tablename__ = "partnerships"
    id: int | None = Field(default=None, primary_key=True)
    type: int = Field(sa_column_args=[CheckConstraint("type IN (1, 2)")])


class PartnershipWrite(PartnershipBase): ...


class PartnershipParticipantRead(BaseModel):
    model_config = {
        "from_attributes": True,
    }
    role: Role = Field(description="1=mate, 2=child, 3=member")


class PartnershipParticipantWrite(PartnershipParticipantRead):
    character_id: int


class PartnershipParticipant(SQLModel, table=True):
    __tablename__ = "partnership_participants"
    __table_args__ = (
        UniqueConstraint(
            "partnership_id", "character_id", name="_partnership_character_uc"
        ),
    )

    partnership_id: int = Field(
        foreign_key="partnerships.id", ondelete="CASCADE", primary_key=True
    )
    character_id: int = Field(
        foreign_key="character.id", ondelete="CASCADE", primary_key=True
    )
    role: int = Field(sa_column_args=[CheckConstraint("role IN (1, 2, 3)")])
