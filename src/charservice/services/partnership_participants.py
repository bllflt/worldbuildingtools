from sqlalchemy import text
from sqlmodel import Session, select

from charservice.models.model import (
    PartnershipParticipant,
    PartnershipParticipantWrite,
)


class PartnershipParticipantService:
    @staticmethod
    def get_participants(session: Session, partnership_id: int) -> list[PartnershipParticipant]:
        """Retrieve all participants for a partnership."""
        PartnershipParticipantService._validate_partnership_exists(
            session, partnership_id
        )
        results = session.exec(
            select(PartnershipParticipant).where(
                PartnershipParticipant.partnership_id == partnership_id
            )
        ).all()
        return results

    @staticmethod
    def get_participant(
        session: Session, partnership_id: int, character_id: int
    ) -> PartnershipParticipant | None:
        """Retrieve a specific participant in a partnership."""
        return session.exec(
            select(PartnershipParticipant).where(
                PartnershipParticipant.partnership_id == partnership_id,
                PartnershipParticipant.character_id == character_id,
            )
        ).one_or_none()

    @staticmethod
    def add_participants(
        session: Session,
        partnership_id: int,
        participants: list[PartnershipParticipantWrite],
    ) -> list[PartnershipParticipant]:
        """Add multiple participants to a partnership."""
        PartnershipParticipantService._validate_partnership_exists(
            session, partnership_id
        )

        for p in participants:
            PartnershipParticipantService._validate_character_exists(
                session, p.character_id
            )

        created_participants = [
            PartnershipParticipant.model_validate(
                p.model_dump() | {"partnership_id": partnership_id}
            )
            for p in participants
        ]
        session.add_all(created_participants)
        session.commit()
        return created_participants

    @staticmethod
    def update_participant(
        session: Session,
        partnership_id: int,
        character_id: int,
        participant: PartnershipParticipantWrite,
    ) -> PartnershipParticipant:
        """Update a participant's role in a partnership."""
        pp = session.exec(
            select(PartnershipParticipant).where(
                PartnershipParticipant.partnership_id == partnership_id,
                PartnershipParticipant.character_id == character_id,
            )
        ).one_or_none()
        if not pp:
            raise ValueError(
                f"Participant not found in partnership {partnership_id}"
            )
        pp.sqlmodel_update(participant)
        session.commit()
        session.refresh(pp)
        return pp

    @staticmethod
    def delete_participant(
        session: Session, partnership_id: int, character_id: int
    ) -> None:
        """Remove a participant from a partnership."""
        pp = session.exec(
            select(PartnershipParticipant).where(
                PartnershipParticipant.partnership_id == partnership_id,
                PartnershipParticipant.character_id == character_id,
            )
        ).one_or_none()
        if not pp:
            raise ValueError(
                f"Participant not found in partnership {partnership_id}"
            )
        session.delete(pp)
        session.commit()

    @staticmethod
    def _validate_partnership_exists(session: Session, partnership_id: int) -> None:
        """Internal helper to validate partnership exists."""
        found = session.exec(
            text("select exists(select 1 from partnerships where id = :pid)"),
            params={"pid": partnership_id},
        ).scalar_one()
        if not found:
            raise ValueError(f"Partnership with id {partnership_id} not found")

    @staticmethod
    def _validate_character_exists(session: Session, character_id: int) -> None:
        """Internal helper to validate character exists."""
        found = session.exec(
            text("select exists(select 1 from character where id = :cid)"),
            params={"cid": character_id},
        ).scalar_one()
        if not found:
            raise ValueError(f"Character with id {character_id} not found")
