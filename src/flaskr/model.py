from typing import List
from typing import Optional

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, String, CheckConstraint
from sqlalchemy.orm import (DeclarativeBase, Mapped, MappedAsDataclass,
                            mapped_column, relationship)
from typing_extensions import Annotated


class Base(DeclarativeBase, MappedAsDataclass):
    pass


db = SQLAlchemy(model_class=Base)


class Character(db.Model):
    __tablename__ = 'character'

    id: Mapped[Annotated[int, mapped_column(
        primary_key=True)]] = mapped_column(init=False)
    name: Mapped[str] = mapped_column(
        CheckConstraint("length(trim(name))>0"),
        nullable=False,
    )
    appearance: Mapped[Optional[str]]
    background:  Mapped[Optional[str]]
    roleplaying: Mapped[List["Roleplaying"]] = relationship(
        back_populates="character", default_factory=list
    )


class Roleplaying(db.Model):
    __tablename__ = 'roleplaying'

    id: Annotated[int, mapped_column(
        primary_key=True)] = mapped_column(init=False)
    characteristic: Mapped[str]
    character_id: Annotated[int, mapped_column(
        ForeignKey("character.id"))] = mapped_column(init=False)
    character: Mapped["Character"] = relationship(
        back_populates='roleplaying', default=None)
