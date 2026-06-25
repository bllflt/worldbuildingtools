from collections.abc import Sequence
from typing import Any

from sqlmodel import Session, select

from charservice.modules.stories.models import Saga, SagaXUser


class SagaService:
    @staticmethod
    def get_permitted_stories(session: Session, user_id: int) -> Sequence[int]:
        """Get a list of story IDs that the user has access to."""
        stmt = select(SagaXUser.saga_id).where(SagaXUser.user_id == user_id)
        return session.exec(stmt).all()

    @staticmethod
    def get_permitted_story_names_by_ids(
        session: Session, permitted_story_ids: Sequence[int]
    ) -> list[dict[str, str | Any | None]]:
        """Get a list of stories with their UUIDs and names."""
        stmt = select(Saga.id, Saga.title).where(Saga.id.in_(permitted_story_ids))
        return [
            {"uuid": saga_id, "name": title}
            for saga_id, title in session.exec(stmt).all()
        ]
