from collections import defaultdict

import pytest
from pytest_unordered import unordered
from sqlmodel import Session, col, select

from charservice.mcp.character_connections import CharacterConnectionsService
from charservice.models.enums import Ptype, RoleCode
from charservice.models.model import Character, Partnership, PartnershipParticipant


class TestCreateCharCon:
    @pytest.mark.parametrize(
        "rc1, r2, ptype",
        [
            (RoleCode.CONCUBINE, RoleCode.MATE, Ptype.LIAISON),
            (RoleCode.LIEGE, RoleCode.RETAINER, Ptype.FACTION),
        ],
    )
    def test_create_char_con(
        self, db_session: Session, rc1: RoleCode, r2: RoleCode, ptype: Ptype
    ) -> None:
        g = Character(story_uuid="test-story", name="G")
        c = Character(story_uuid="test-story", name="C")

        db_session.add_all([g, c])
        db_session.commit()

        CharacterConnectionsService.create_pairwise_connection(
            db_session,
            g.id,
            rc1,
            c.id,  # type: ignore
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
        g = Character(story_uuid="test-story", name="G")
        f = Partnership(type=Ptype.FACTION, name="Guild")
        db_session.add_all([g, f])
        db_session.commit()

        CharacterConnectionsService.create_faction_connection(
            db_session,
            g.id, # type: ignore
            f.id, # type: ignore
        )

        partnership = db_session.exec(
            select(Partnership).where(Partnership.name == "Guild")
        ).one_or_none()
        assert partnership is not None
        assert partnership.type == int(Ptype.FACTION)
        assert partnership.participants == [
            PartnershipParticipant(
                partnership_id=partnership.id, # type: ignore
                character_id=g.id,             # type: ignore 
                role_code=RoleCode.MEMBER,
            )
        ]
