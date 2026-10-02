from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from sqlmodel import Session, select

from charservice.modules.arsmagica.models import Virtue
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
