from typing import List
from typing import Optional

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, CheckConstraint
from sqlalchemy.orm import (DeclarativeBase, Mapped, MappedAsDataclass,
                            mapped_column, relationship)
from typing_extensions import Annotated


class Base(DeclarativeBase, MappedAsDataclass):
    pass


db = SQLAlchemy(model_class=Base)


from sqlalchemy.engine import Engine
from sqlalchemy import event


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class Character(db.Model):
    __tablename__ = 'character'

    id: Mapped[Annotated[int, mapped_column(
        primary_key=True)]] = mapped_column(init=False)
    name: Mapped[str] = mapped_column(
        CheckConstraint("length(trim(name))>0"),
        nullable=False,
    )
    appearance: Mapped[Optional[str]] = mapped_column(default=None)
    background:  Mapped[Optional[str]] = mapped_column(default=None)
    roleplaying: Mapped[List["Roleplaying"]] = relationship(
        back_populates="character", default_factory=list,
        cascade="all, delete",
        passive_deletes=True,
    )
    images: Mapped[List["Image"]] = relationship(
        default_factory=list,
        cascade="all, delete",
        passive_deletes=True,
    )


class Roleplaying(db.Model):
    __tablename__ = 'roleplaying'

    id: Annotated[int, mapped_column(
        primary_key=True)] = mapped_column(init=False)
    characteristic: Mapped[str]
    character_id: Annotated[int, mapped_column(
        ForeignKey("character.id", ondelete="CASCADE")
        )] = mapped_column(init=False)
    character: Mapped["Character"] = relationship(
        back_populates='roleplaying', default=None)


class Image(db.Model):
    __tablename__ = 'images'

    id: Annotated[int, mapped_column(
        primary_key=True)] = mapped_column(init=False)
    character_id: Annotated[int, mapped_column(
        ForeignKey("character.id", ondelete="SET NULL")
    )] = mapped_column(init=False, nullable=True)
    url: Mapped[str] = mapped_column(
        CheckConstraint("length(trim(url))>0"),
        nullable=False,
    )