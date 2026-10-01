from collections.abc import Sequence

from sqlmodel import Session, select

from charservice.modules.arsmagica.models import Virtue


class VirtueService:
    @staticmethod
    def get_virtues(session: Session) -> Sequence[Virtue]:
        stmt = select(Virtue)
        return session.exec(stmt).all()

    @staticmethod
    def get_virtue_by_name(session: Session, name: str) -> Virtue | None:
        stmt = select(Virtue).where(Virtue.name == name)
        return session.exec(stmt).one_or_none()
