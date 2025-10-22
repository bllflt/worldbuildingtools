from typing import List, Optional

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import (DeclarativeBase, Mapped, MappedAsDataclass,
                            mapped_column, relationship)
from typing_extensions import Annotated


class Base(DeclarativeBase, MappedAsDataclass):
    pass


db = SQLAlchemy(model_class=Base)

from sqlalchemy import event  # pylint: disable=wrong-import-position
from sqlalchemy.engine import Engine  # pylint: disable=wrong-import-position


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, _connection_record):
    # the sqlite3 driver will not set PRAGMA foreign_keys
    # if autocommit=False; set to True temporarily
    ac = dbapi_connection.autocommit
    dbapi_connection.autocommit = True

    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

    # restore previous autocommit setting
    dbapi_connection.autocommit = ac


class Character(db.Model):
    __tablename__ = 'character'

    id: Mapped[Annotated[int, mapped_column(
        primary_key=True)]] = mapped_column(init=False)
    name: Mapped[str] = mapped_column(
        CheckConstraint("length(trim(name))>0"),
        nullable=False,
        unique=True,
    )
    appearance: Mapped[Optional[str]] = mapped_column(default=None)
    background:  Mapped[Optional[str]] = mapped_column(default=None)
    sex: Mapped[Annotated[int,
                          mapped_column()]] = mapped_column(
        default=9)
    # "ISO/IEC 5218
    UNKNOWN = 0
    MALE = 1
    FEMALE = 2
    NA = 9
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
    characteristic: Mapped[str] = mapped_column(
        CheckConstraint("length(trim(characteristic))>0"),
        nullable=False,
    )
    character_id: Annotated[int, mapped_column(
        ForeignKey("character.id", ondelete="CASCADE"),
        nullable=False
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
    uri: Mapped[str] = mapped_column(
        CheckConstraint("length(trim(uri))>0"),
        nullable=False,
    )


class Partnership(db.Model):
    __tablename__ = 'partnerships'

    id: Annotated[int, mapped_column(
        primary_key=True)] = mapped_column(init=False)
    type: Annotated[int, mapped_column()] = mapped_column()
    MARRIAGE = 1
    CONCUBINAGE = 2
    COHABITATION = 3
    ENGAGEMENT = 4
    LIAISON = 5
    
    OTHER = 99
    start_date: Mapped[Optional[str]] = mapped_column(default=None)
    end_date: Mapped[Optional[str]] = mapped_column(default=None)
    is_primary: Mapped[Optional[bool]] = mapped_column(default=False)


class PartnershipParticipant(db.Model):
    __tablename__ = 'partnership_participants'
    __table_args__ = (UniqueConstraint('partnership_id', 'character_id',
                                       name='_partnership_character_uc'),)

    partnership_id: Annotated[int, mapped_column(
        ForeignKey("partnerships.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )] = mapped_column()
    character_id: Annotated[int, mapped_column(
        ForeignKey("character.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )] = mapped_column()
    role: Mapped[Optional[str]] = mapped_column(default=None)


class Offspring(db.Model):
    __tablename__ = 'offspring'
    __table_args__ = (UniqueConstraint('partnership_id', 'character_id',
                                       name='_partnership_child_uc'),)

    partnership_id: Annotated[int, mapped_column(
        ForeignKey("partnerships.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )] = mapped_column()
    character_id: Annotated[int, mapped_column(
        ForeignKey("character.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True
    )] = mapped_column()
