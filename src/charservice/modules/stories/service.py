from collections.abc import Sequence

from sqlmodel import Session, select

from charservice.modules.stories.models import SagaXUser


class SagaService:
    @staticmethod
    def get_permitted_stories(session: Session, user_id: int) -> Sequence[int]:
        """Get a list of story IDs that the user has access to."""
        stmt = select(SagaXUser.saga_id).where(SagaXUser.user_id == user_id)
        return session.exec(stmt).all()
