from sqlmodel import Session

from charservice.models.enums import Ptype, RoleCode
from charservice.models.model import Character, Partnership, PartnershipParticipant
from charservice.services.partnership_participants import PartnershipParticipantService


class TestLiaisonThings:
    def test_find_laison_containing_characters(self, db_session: Session) -> None:
        g1 = Character(name="G1")
        g2 = Character(name="G2")
        g3 = Character(name="G3")
        p1 = Partnership(type=Ptype.LIAISON)
        p2 = Partnership(type=Ptype.FACTION, name="L2")
        db_session.add_all([g1, g2, g3, p1, p2])
        db_session.commit()
        p1pp1 = PartnershipParticipant(
            partnership_id=p1.id, character_id=g1.id, role_code=RoleCode.CONCUBINE
        )
        p1pp2 = PartnershipParticipant(
            partnership_id=p1.id, character_id=g2.id, role_code=RoleCode.MATE
        )
        p2pp1 = PartnershipParticipant(
            partnership_id=p2.id, character_id=g1.id, role_code=RoleCode.MEMBER
        )

        db_session.add_all([p1pp1, p1pp2, p2pp1])
        db_session.commit()

        assert (
            PartnershipParticipantService.find_laison_containing_characters(
                db_session, [g1.id, g2.id]
            )
            == p1.id
        )
        assert (
            PartnershipParticipantService.find_laison_containing_characters(
                db_session, [g1.id, g3.id]
            )
            is None
        )
