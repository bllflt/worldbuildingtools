from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlmodel import Session, SQLModel, select

from charservice.modules.arsmagica.models import (
    CharacterXFlaw,
    CharacterXVirtue,
    Flaw,
    Virtue,
)
from charservice.services.query import BaseQuery, build_query_statement

TraitT = TypeVar("TraitT", bound=SQLModel)


@dataclass(slots=True)
class VirtueQuery(BaseQuery):
    """Query parameters for retrieving Virtue objects."""


@dataclass(slots=True)
class FlawQuery(BaseQuery):
    """Query parameters for retrieving Flaw objects."""


class CharacterTraitService(Generic[TraitT]):
    model: type[TraitT]
    association_model: type[SQLModel]
    name_field: str
    character_id_field: str
    association_field: str
    trait_name: str

    @classmethod
    def get_traits(
        cls, session: Session, query: BaseQuery | None = None
    ) -> Sequence[Any]:
        if query is None:
            query = BaseQuery()
        stmt = build_query_statement(
            cls.model,
            fields=query.fields,
            sort=query.sort,
            name=query.name,
        )
        return session.exec(stmt).all()

    @classmethod
    def get_trait_by_name(cls, session: Session, name: str) -> TraitT | None:
        stmt = select(cls.model).where(getattr(cls.model, cls.name_field) == name)
        return session.exec(stmt).one_or_none()

    @classmethod
    def get_traits_of_character(
        cls, session: Session, character_id: UUID
    ) -> Sequence[str]:
        stmt = select(getattr(cls.association_model, cls.association_field)).where(
            getattr(cls.association_model, cls.character_id_field) == character_id
        )
        return session.exec(stmt).all()

    @classmethod
    def add_trait_to_character(
        cls, session: Session, character_id: UUID, trait: str
    ) -> None:
        if cls.get_trait_by_name(session, trait) is None:
            raise ValueError(f"{cls.trait_name.capitalize()} '{trait}' does not exist.")

        trait_field = getattr(cls.association_model, cls.association_field)
        stmt = select(cls.association_model).where(
            getattr(cls.association_model, cls.character_id_field) == character_id,
            trait_field == trait,
        )
        existing_entry = session.exec(stmt).one_or_none()

        if existing_entry:
            raise ValueError(
                f"Character '{character_id}' already has the "
                f"{cls.trait_name} '{trait}'."
            )

        new_entry = cls.association_model(
            **{"character_id": character_id, cls.association_field: trait}
        )
        session.add(new_entry)
        session.commit()

    @classmethod
    def remove_trait_from_character(
        cls, session: Session, character_id: UUID, trait: str
    ) -> None:
        stmt = select(cls.association_model).where(
            getattr(cls.association_model, cls.character_id_field) == character_id,
            getattr(cls.association_model, cls.association_field) == trait,
        )
        entry = session.exec(stmt).one_or_none()

        if not entry:
            raise ValueError(
                f"Character '{character_id}' does not have the "
                f"{cls.trait_name} '{trait}'."
            )

        session.delete(entry)
        session.commit()


class VirtueService(CharacterTraitService[Virtue]):
    model = Virtue
    association_model = CharacterXVirtue
    name_field = "name"
    character_id_field = "character_id"
    association_field = "virtue"
    trait_name = "virtue"

    @classmethod
    def get_virtues(
        cls, session: Session, query: VirtueQuery | None = None
    ) -> Sequence[Any]:
        return cls.get_traits(session, query)

    @classmethod
    def get_virtue_by_name(cls, session: Session, name: str) -> Virtue | None:
        return cls.get_trait_by_name(session, name)

    @classmethod
    def get_virtues_of_character(
        cls, session: Session, character_id: UUID
    ) -> Sequence[str]:
        return cls.get_traits_of_character(session, character_id)

    @classmethod
    def update_virtue_of_character(
        cls, session: Session, character_id: UUID, virtue: str
    ) -> None:
        cls.add_trait_to_character(session, character_id, virtue)

    @classmethod
    def remove_virtue_of_character(
        cls, session: Session, character_id: UUID, virtue: str
    ) -> None:
        cls.remove_trait_from_character(session, character_id, virtue)


class FlawService(CharacterTraitService[Flaw]):
    model = Flaw
    association_model = CharacterXFlaw
    name_field = "name"
    character_id_field = "character_id"
    association_field = "flaw"
    trait_name = "flaw"

    @classmethod
    def get_flaws(
        cls, session: Session, query: FlawQuery | None = None
    ) -> Sequence[Any]:
        return cls.get_traits(session, query)

    @classmethod
    def get_flaw_by_name(cls, session: Session, name: str) -> Flaw | None:
        return cls.get_trait_by_name(session, name)

    @classmethod
    def get_flaws_of_character(
        cls, session: Session, character_id: UUID
    ) -> Sequence[str]:
        return cls.get_traits_of_character(session, character_id)

    @classmethod
    def update_flaw_of_character(
        cls, session: Session, character_id: UUID, flaw: str
    ) -> None:
        cls.add_trait_to_character(session, character_id, flaw)

    @classmethod
    def remove_flaw_of_character(
        cls, session: Session, character_id: UUID, flaw: str
    ) -> None:
        cls.remove_trait_from_character(session, character_id, flaw)