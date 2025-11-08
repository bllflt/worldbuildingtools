from dataclasses import dataclass
from typing import Optional

from apifast.model import Character
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select


@dataclass(slots=True)
class CharacterQuery:
    """Query parameters for retrieving Character objects."""

    sort: Optional[str] = None
    name: Optional[str] = None
    fields: Optional[set[str]] = None


class CharacterService:
    @staticmethod
    def get_characters(session: Session, query: CharacterQuery | None = None):
        """Retrieve characters with optional sorting, filtering, and field selection."""
        query = query or CharacterQuery()
        stmt = select(Character)

        if query.fields:
            stmt = select(*(getattr(Character, f) for f in query.fields))

        if query.sort:
            stmt = stmt.order_by(getattr(Character, query.sort))

        if query.name:
            stmt = stmt.where(Character.name.icontains(query.name))

        if not query.fields:
            stmt = stmt.options(
                selectinload(Character.roleplaying_attributes),
                selectinload(Character.image_attributes),
            )

        return session.exec(stmt).all()

    @staticmethod
    def get_character_by_id(session: Session, character_id: int) -> Character:
        """Retrieve a character by its ID."""
        return session.get(
            Character,
            character_id,
            options=(
                selectinload(Character.roleplaying_attributes),
                selectinload(Character.image_attributes),
            ),
        )
