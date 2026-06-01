from collections import defaultdict

import pytest
from pytest_unordered import unordered
from sqlmodel import Session, col, select

from charservice.mcp.character_connections import CharacterConnectionsService
from charservice.models.enums import Ptype, RoleCode
from charservice.models.model import Character, Partnership, PartnershipParticipant
from charservice.modules.social.schemas import Association, Member


class TestCreateCharCon:
    @pytest.mark.parametrize(
        "rc1, r2, ptype",
        [
            (RoleCode.MATE, RoleCode.CONCUBINE, Ptype.LIAISON),
            (RoleCode.LIEGE, RoleCode.RETAINER, Ptype.FACTION),
        ],
    )
    def test_create_char_con(
        self, db_session: Session, rc1: RoleCode, r2: RoleCode, ptype: Ptype
    ) -> None:
        g = Character(name="G")
        c = Character(name="C")

        db_session.add_all([g, c])
        db_session.commit()

        CharacterConnectionsService.create_connection(
            db_session,
            Member(character_id=str(g.id), role_code=rc1),
            Member(character_id=str(c.id), role_code=r2),
        )

        got = defaultdict(dict)
        results = db_session.exec(
            select(Partnership, PartnershipParticipant)
            .join(PartnershipParticipant)
            .where(col(PartnershipParticipant.character_id).in_([g.id, c.id]))
        )
        for partnership, participant in results:
            got[partnership.id]["type"] = partnership.type
            if "participants" not in got[partnership.id]:
                got[partnership.id]["participants"] = []
            got[partnership.id]["participants"].append(
                {
                    "character_id": participant.character_id,
                    "role_code": participant.role_code,
                }
            )

        assert len(list(got.values())) == 1
        assert list(got.values())[0]["type"] == int(ptype)
        assert list(got.values())[0]["participants"] == unordered(
            [
                {"character_id": g.id, "role_code": rc1},
                {"character_id": c.id, "role_code": r2},
            ]
        )

    def test_create_char_con_faction(self, db_session: Session) -> None:
        g = Character(name="G")
        db_session.add(g)
        db_session.commit()

        CharacterConnectionsService.create_connection(
            db_session,
            Member(character_id=str(g.id), role_code=RoleCode.MEMBER),
            Association(name="Guild"),
        )

        partnership = db_session.exec(select(Partnership).where(Partnership.name == "Guild")).one_or_none()
        assert partnership is not None
        assert partnership.type == int(Ptype.FACTION)
        assert partnership.participants == [
            PartnershipParticipant(
                partnership_id=partnership.id,
                character_id=g.id,
                role_code=RoleCode.MEMBER,
            )
        ]
    def test_create_char_con_faction_exists(self, db_session: Session) -> None:
        g1 = Character(name="G1")
        g2 = Character(name="G2")
        db_session.add_all([g1, g2])
        db_session.commit()

        # Create the first connection to the faction
        CharacterConnectionsService.create_connection(
            db_session,
            Member(character_id=str(g1.id), role_code=RoleCode.MEMBER),
            Association(name="Guild"),
        )

        # Create the second connection to the same faction
        CharacterConnectionsService.create_connection(
            db_session,
            Member(character_id=str(g2.id), role_code=RoleCode.MEMBER),
            Association(name="Guild"),
        )

        partnership = db_session.exec(select(Partnership).where(Partnership.name == "Guild")).one_or_none()
        assert partnership is not None
        assert partnership.type == int(Ptype.FACTION)
        assert partnership.participants == unordered([
            PartnershipParticipant(
                partnership_id=partnership.id,
                character_id=g1.id,
                role_code=RoleCode.MEMBER,
            ),
            PartnershipParticipant(
                partnership_id=partnership.id,
                character_id=g2.id,
                role_code=RoleCode.MEMBER,
            )
        ])