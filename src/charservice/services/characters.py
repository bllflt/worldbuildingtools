from dataclasses import dataclass
from typing import Optional

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from charservice.models.model import (
    Character,
    CharacterCreate,
    CharacterWrite,
    Image,
    Roleplaying,
)


@dataclass(slots=True)
class CharacterQuery:
    """Query parameters for retrieving Character objects."""

    story_uuid: str
    sort: Optional[str] = None
    name: Optional[str] = None
    fields: Optional[set[str]] = None


class CharacterService:
    @staticmethod
    def get_characters(session: Session, query: CharacterQuery) -> list[Character]:
        """Retrieve characters with optional sorting, filtering, and field selection."""
        stmt = select(Character).where(Character.story_uuid == query.story_uuid)

        if query.fields:
            stmt = select(*(getattr(Character, f) for f in query.fields))
            stmt = stmt.where(Character.story_uuid == query.story_uuid)

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
    def get_character_by_id(
        session: Session, character_id: int, permitted_stories: set[str] | None = None
    ) -> Character | None:
        """Retrieve a character by its ID."""
        if permitted_stories is None:
            return session.get(
                Character,
                character_id,
                options=(
                    selectinload(Character.roleplaying_attributes),
                    selectinload(Character.image_attributes),
                ),
            )
        else:
            return session.exec(
                select(Character)
                .where(
                    Character.id == character_id,
                    Character.story_uuid.in_(permitted_stories),
                )
                .options(
                    selectinload(Character.roleplaying_attributes),
                    selectinload(Character.image_attributes),
                )
            ).one_or_none()

    @staticmethod
    def create_character(
        session: Session, story_uuid: str, character: CharacterCreate
    ) -> Character:
        """Create a new character."""
        character_data = character.model_dump(exclude={"attributes", "images"})
        db_character = Character.model_validate(character_data)
        db_character.story_uuid = story_uuid
        db_character.roleplaying_attributes = [
            Roleplaying(characteristic=attr) for attr in character.roleplaying
        ]
        db_character.image_attributes = [Image(uri=img) for img in character.images]

        session.add(db_character)
        session.commit()
        return db_character

    @staticmethod
    def update_character(
        session: Session,
        character_id: int,
        character: CharacterWrite,
        permitted_stories: set[str] | None,
    ) -> None:
        """Update an existing character."""
        db_character = CharacterService.get_character_by_id(
            session, character_id, permitted_stories
        )
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
                db_character.roleplaying_attributes.append(
                    Roleplaying(characteristic=attr)
                )

        old_images = [i.uri for i in db_character.image_attributes]
        for img in db_character.image_attributes:
            if img.uri not in character.images:
                img.character_id = None
        for img in character.images:
            if img not in old_images:
                db_character.image_attributes.append(Image(uri=img))

        session.commit()

    @staticmethod
    def delete_character(
        session: Session, character_id: int, permitted_stories: set[str] | None
    ) -> None:
        """Delete a character."""
        character = CharacterService.get_character_by_id(
            session, character_id, permitted_stories
        )
        if not character:
            raise ValueError(f"Character with id {character_id} not found")
        session.delete(character)
        session.commit()
