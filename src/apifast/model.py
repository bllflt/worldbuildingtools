import enum

from pydantic import BaseModel
from pydantic import Field as PydanticField
from pydantic import computed_field
from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel
from typing_extensions import Annotated


# ISO/IEC 5218
class Sex(enum.IntEnum):
    UNKNOWN = 0
    MALE = 1
    FEMALE = 2
    NA = 9

class Character(SQLModel, table=True):
    __tablename__ = "character"

    id: int | None = Field(default=None, primary_key=True)
    name: Annotated[str, Field(
          min_length=1,
          index=True,
          unique=True,
          sa_column_args=[CheckConstraint("length(trim(name)) > 0")],
          )]
    background: str | None = Field(default=None)
    appearance: str | None = Field(default=None)
    sex: Annotated[int, Field(
        default=Sex.NA,
        sa_column_args=[CheckConstraint("sex IN (0, 1, 2, 9)")],
    )]
    roleplaying_attributes: list["Roleplaying"] = Relationship(
        back_populates="character_link",
        sa_relationship_kwargs={"cascade": "all, delete",
                                "passive_deletes": True})


class Roleplaying(SQLModel, table=True):
    __tablename__ = "roleplaying"

    id: int | None = Field(default=None, primary_key=True)
    characteristic: Annotated[str, Field(
          min_length=1,
          sa_column_args=[CheckConstraint("length(trim(characteristic)) > 0")],
    )]
    character_id: int | None = Field(
        default=None,
        foreign_key="character.id",
        sa_column_args=[ForeignKey("character.id", ondelete="CASCADE")]
    )
    character_link: "Character" = Relationship(back_populates="roleplaying_attributes")

class CharacterRead(BaseModel):
    # This model is for reading data. It mirrors Character's fields
    # but uses a computed_field to reshape the 'attributes' relationship.
    id: int
    name: str
    background: str | None
    appearance: str | None
    sex: int
    roleplaying_attributes: list["Roleplaying"] = PydanticField(exclude=True)

    @computed_field(return_type=list[str])
    @property
    def attributes(self) -> list[str]:
        """Pluck the 'characteristic' from each Roleplaying object."""
        return [rp.characteristic for rp in self.roleplaying_attributes]

class Image(SQLModel, table=True):
    __tablename__ = "images"

    id: int | None = Field(default=None, primary_key=True)
    character_id: int | None = Field(
        default=None,
        foreign_key="character.id",
        sa_column_args=[ForeignKey("character.id", ondelete="SET NULL")]
    )
    uri: Annotated[str, Field( 
          min_length=1,
          sa_column_args=[CheckConstraint("length(trim(uri)) > 0")]
    )]


class Partnership(SQLModel, table=True):
    __tablename__ = 'partnerships'

    id: int | None = Field(default=None, primary_key=True)
    type: int
    start_date: str | None = Field(default=None)
    end_date: str | None = Field(default=None)
    is_primary: bool | None = Field(default=False)
    legitimate: bool | None = Field(default=False)
    name: str | None = Field(default=None)


class PartnershipParticipant(SQLModel, table=True):
    __tablename__ = 'partnership_participants'
    __table_args__ = (
        UniqueConstraint('partnership_id', 'character_id', name='_partnership_character_uc'),
    )

    partnership_id: int = Field(
        foreign_key="partnerships.id",
        sa_column_args=[ForeignKey("partnerships.id", ondelete="CASCADE")],
        primary_key=True)
    character_id: int = Field(
        foreign_key="character.id",
        sa_column_args=[ForeignKey("character.id", ondelete="CASCADE")],
        primary_key=True)
    role: int = Field(default=None)
    partnership: "Partnership" = Relationship()
    character: "Character" = Relationship()
