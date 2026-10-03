from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlmodel import Session, select

from charservice.modules.arsmagica.models import CharacterXVirtue, Virtue
from charservice.services.query import BaseQuery, build_query_statement


@dataclass(slots=True)
class VirtueQuery(BaseQuery):
    """Query parameters for retrieving Virtue objects."""

    pass


class VirtueService:
    @staticmethod
    def get_virtues(
        session: Session, query: VirtueQuery | None = None
    ) -> Sequence[Any]:
        if query is None:
            query = VirtueQuery()
        stmt = build_query_statement(
            Virtue,
            fields=query.fields,
            sort=query.sort,
            name=query.name,
        )
        return session.exec(stmt).all()

    @staticmethod
    def get_virtue_by_name(session: Session, name: str) -> Virtue | None:
        stmt = select(Virtue).where(Virtue.name == name)
        return session.exec(stmt).one_or_none()

    @staticmethod
    def get_virtues_of_character(session: Session, character_id: UUID) -> Sequence[Any]:
        stmt = select(CharacterXVirtue.virtue).where(
            CharacterXVirtue.character_id == character_id
        )
        return session.exec(stmt).all()

    @staticmethod
    def update_virtue_of_character(
        session: Session, character_id: UUID, virtue: str
    ) -> None:
        # Check if the virtue exists
        virtue_obj = VirtueService.get_virtue_by_name(session, virtue)
        if not virtue_obj:
            raise ValueError(f"Virtue '{virtue}' does not exist.")

        # Check if the character already has this virtue
        stmt = select(CharacterXVirtue).where(
            CharacterXVirtue.character_id == character_id,
            CharacterXVirtue.virtue == virtue,
        )
        existing_entry = session.exec(stmt).one_or_none()

        if existing_entry:
            # If the entry exists, we can choose to either do nothing or raise an error
            raise ValueError(
                f"Character '{character_id}' already has the virtue '{virtue}'."
            )

        # Add the new virtue to the character
        new_entry = CharacterXVirtue(character_id=character_id, virtue=virtue)
        session.add(new_entry)
        session.commit()

    @staticmethod
    def remove_virtue_of_character(session: Session, character_id: UUID, virtue: str) -> None:
        stmt = select(CharacterXVirtue).where(
            CharacterXVirtue.character_id == character_id,
            CharacterXVirtue.virtue == virtue,
        )
        entry = session.exec(stmt).one_or_none()

        if not entry:
            raise ValueError(
                f"Character '{character_id}' does not have the virtue '{virtue}'."
            )

        session.delete(entry)
        session.commit()