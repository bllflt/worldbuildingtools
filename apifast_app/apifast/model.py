import enum

from pydantic import BaseModel
from pydantic import Field as PydanticField
from pydantic import computed_field
from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


# ISO/IEC 5218
class Sex(enum.IntEnum):
    UNKNOWN = 0
    MALE = 1
    FEMALE = 2
    NA = 9


class CharacterBase(BaseModel):
    name: str
    background: str | None = None
    appearance: str | None = None
    sex: Sex = Sex.NA


class Character(SQLModel, CharacterBase, table=True):
    sex: int | None = Field(
        default=Sex.NA, sa_column_args=[CheckConstraint("sex IN (0, 1, 2, 9)")]
    )
    id: int | None = Field(default=None, primary_key=True)

    roleplaying_attributes: list["Roleplaying"] = Relationship(
        back_populates="character_link",
        sa_relationship_kwargs={"cascade": "all, delete", "passive_deletes": True},
    )
    image_attributes: list["Image"] = Relationship(
        back_populates="character_link",
        sa_relationship_kwargs={"cascade": "all, delete", "passive_deletes": True},
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


class CharacterCreate(CharacterBase):
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
        default=None,
        foreign_key="character.id",
        sa_column_args=[ForeignKey("character.id", ondelete="CASCADE")],
    )
    character_link: "Character" = Relationship(back_populates="roleplaying_attributes")


class Image(SQLModel, table=True):
    __tablename__ = "images"

    id: int | None = Field(default=None, primary_key=True)
    character_id: int | None = Field(
        default=None,
        foreign_key="character.id",
        sa_column_args=[ForeignKey("character.id", ondelete="SET NULL")],
    )
    uri: str | None = Field(
        default=None,
        min_length=1,
        sa_column_args=[CheckConstraint("length(trim(uri)) > 0")],
    )
    character_link: "Character" = Relationship(back_populates="")


class Partnership(SQLModel, table=True):
    __tablename__ = "partnerships"

    id: int | None = Field(default=None, primary_key=True)
    type: int
    start_date: str | None = Field(default=None)
    end_date: str | None = Field(default=None)
    is_primary: bool | None = Field(default=False)
    legitimate: bool | None = Field(default=False)
    name: str | None = Field(default=None)


class PartnershipParticipant(SQLModel, table=True):
    __tablename__ = "partnership_participants"
    __table_args__ = (
        UniqueConstraint(
            "partnership_id", "character_id", name="_partnership_character_uc"
        ),
    )

    partnership_id: int = Field(
        foreign_key="partnerships.id",
        sa_column_args=[ForeignKey("partnerships.id", ondelete="CASCADE")],
        primary_key=True,
    )
    character_id: int = Field(
        foreign_key="character.id",
        sa_column_args=[ForeignKey("character.id", ondelete="CASCADE")],
        primary_key=True,
    )
    role: int = Field(default=None)
    partnership: "Partnership" = Relationship()
    character: "Character" = Relationship()
