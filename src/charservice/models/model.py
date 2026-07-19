from uuid import UUID

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel, text

from charservice.models.enums import Ptype, RoleCode, Sex
from charservice.models.schemas import CharacterBase, PartnershipBase


class Character(SQLModel, CharacterBase, table=True):
    __table_args__ = (
        UniqueConstraint("story_uuid", "name"),
        CheckConstraint("length(trim(name)) > 0"),
    )

    sex: int | None = Field(
        default=Sex.NA, sa_column_args=[CheckConstraint("sex IN (0, 1, 2, 9)")]
    )
    id: UUID | None = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"server_default": text("uuidv7()")},
    )
    story_uuid: str = Field(default=None)

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


class Roleplaying(SQLModel, table=True):
    __tablename__ = "roleplaying"  # type: ignore[override]

    id: int | None = Field(default=None, primary_key=True)
    characteristic: str | None = Field(
        default=None,
        min_length=1,
        sa_column_args=[CheckConstraint("length(trim(characteristic)) > 0")],
    )
    character_id: UUID | None = Field(
        default=None, foreign_key="character.id", ondelete="CASCADE"
    )
    character_link: "Character" = Relationship(back_populates="roleplaying_attributes")


class Image(SQLModel, table=True):
    __tablename__ = "images"  # type: ignore[override]

    id: int | None = Field(default=None, primary_key=True)
    character_id: UUID | None = Field(
        default=None,
        foreign_key="character.id",
        ondelete="SET NULL",
    )
    uri: str = Field(
        min_length=1,
        unique=True,
        sa_column_args=[CheckConstraint("length(trim(uri)) > 0")],
    )
    character_link: "Character" = Relationship(back_populates="image_attributes")


class Partnership(SQLModel, PartnershipBase, table=True):
    __tablename__ = "partnerships"  # type: ignore[override]
    id: int | None = Field(default=None, primary_key=True)
    type: int = Field(sa_column_args=[CheckConstraint("type IN (1, 2)")])
    participants: list["PartnershipParticipant"] = Relationship(cascade_delete=True)


class Role(SQLModel, table=True):
    __tablename__ = "roles"  # type: ignore[override]
    code: str = Field(default=None, primary_key=True)
    description: str | None = None


class PartnershipParticipant(SQLModel, table=True):
    __tablename__ = "partnership_participants"  # type: ignore[override]
    __table_args__ = (
        UniqueConstraint(
            "partnership_id", "character_id", name="_partnership_character_uc"
        ),
    )

    partnership_id: int = Field(
        foreign_key="partnerships.id", ondelete="CASCADE", primary_key=True
    )
    character_id: UUID = Field(
        foreign_key="character.id", ondelete="CASCADE", primary_key=True
    )
    role_code: str = Field(foreign_key="roles.code", ondelete="CASCADE")
