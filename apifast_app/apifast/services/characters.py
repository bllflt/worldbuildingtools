from dataclasses import dataclass
from typing import Optional

from apifast.model import Character, CharacterWrite, Image, Roleplaying
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

    @staticmethod
    def create_character(session: Session, character: CharacterWrite) -> Character:
        """Create a new character."""
        character_data = character.model_dump(exclude={"attributes", "images"})
        db_character = Character.model_validate(character_data)
        db_character.roleplaying_attributes = [
            Roleplaying(characteristic=attr) for attr in character.roleplaying
        ]
        db_character.image_attributes = [Image(uri=img) for img in character.images]

        session.add(db_character)
        session.commit()
        return db_character

    @staticmethod
    def update_character(
        session: Session, character_id: int, character: CharacterWrite
    ) -> Character:
        """Update an existing character."""
        db_character = CharacterService.get_character_by_id(session, character_id)
        if not db_character:
            raise ValueError(f"Character with id {character_id} not found")

        update_data = character.model_dump(exclude={"roleplaying", "images"})
        for key, value in update_data.items():
            setattr(db_character, key, value)

        old_attributes = [i.characteristic for i in db_character.roleplaying_attributes]     
        for attr in db_character.roleplaying_attributes:
            if attr.characteristic not in character.roleplaying:
                session.delete(attr)
        for attr in character.roleplaying:
            if attr not in old_attributes:
                db_character.roleplaying_attributes.append(Roleplaying(characteristic=attr))
        
        old_images = [i.uri for i in db_character.image_attributes]
        for img in db_character.image_attributes:
            if img.uri not in character.images:
                img.character_id = None
        for img in character.images:
            if img not in old_images:
                db_character.image_attributes.append(Image(uri=img))

        session.commit()

    @staticmethod
    def delete_character(session: Session, character_id: int) -> None:
        """Delete a character."""
        character = session.get(Character, character_id)
        if not character:
            raise ValueError(f"Character with id {character_id} not found")
        session.delete(character)
        session.commit()
