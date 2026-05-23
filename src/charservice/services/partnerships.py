from dataclasses import dataclass
from typing import Optional

from charservice.models.model import Partnership, PartnershipWrite, Ptype
from sqlmodel import Session, select


@dataclass(slots=True)
class PartnershipQuery:
    """Query parameters for retrieving Partnership objects."""

    faction_only: Optional[bool] = None
    partnership_type: Optional[int] = None


class PartnershipService:
    @staticmethod
    def get_partnerships(
        session: Session, query: PartnershipQuery | None = None
    ) -> list[Partnership]:
        """Retrieve partnerships with optional filtering by type/faction."""
        query = query or PartnershipQuery()
        stmt = select(Partnership)

        if query.faction_only:
            stmt = stmt.where(
                Partnership.type == Ptype.FACTION, Partnership.name.is_not(None)
            )

        if query.partnership_type:
            stmt = stmt.where(Partnership.type == query.partnership_type)

        return session.exec(stmt).all()

    @staticmethod
    def get_partnership_by_id(
        session: Session, partnership_id: int
    ) -> Partnership | None:
        """Retrieve a partnership by its ID."""
        return session.get(Partnership, partnership_id)

    @staticmethod
    def create_partnership(session: Session, partnership: PartnershipWrite) -> Partnership:
        """Create a new partnership."""
        db_partnership = Partnership.model_validate(partnership.model_dump())
        session.add(db_partnership)
        session.commit()
        session.refresh(db_partnership)
        return db_partnership

    @staticmethod
    def update_partnership(
        session: Session, partnership_id: int, partnership: PartnershipWrite
    ) -> Partnership:
        """Update an existing partnership."""
        db_partnership = session.get(Partnership, partnership_id)
        if not db_partnership:
            raise ValueError(f"Partnership with id {partnership_id} not found")

        db_partnership.sqlmodel_update(partnership)
        session.commit()
        session.refresh(db_partnership)
        return db_partnership

    @staticmethod
    def delete_partnership(session: Session, partnership_id: int) -> None:
        """Delete a partnership."""
        partnership = session.get(Partnership, partnership_id)
        if not partnership:
            raise ValueError(f"Partnership with id {partnership_id} not found")
        session.delete(partnership)
        session.commit()
