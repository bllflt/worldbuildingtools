import json
from typing import List

from sqlmodel import select, text

from charservice.db import Session
from charservice.models.enums import Ptype
from charservice.models.model import (
    Partnership,
    PartnershipParticipant,
    SocialConnection,
)
from charservice.modules.social.schemas import Member, Association
from charservice.models.enums import RoleCode

class CharacterConnectionsService:
    @staticmethod
    def get_connections_by_character_id(
        session: Session, character_id: int, depth: int
    ) -> List[SocialConnection]:
        """
        Retrieve social connections for a character up to the specified depth.

        Args:
            session: Database session
            character_id: ID of the character
            depth: Degree of social graph to return (0-3)

        Returns:
            List of SocialConnection objects
        """
        rows = (
            session.execute(
                text("""
WITH RECURSIVE

-- start character
start_char AS (
  SELECT :cid AS id
),

-- expand to N degrees (depth)
related(id, depth) AS (
  SELECT id, 0 FROM start_char
  UNION
  SELECT pp2.character_id, r.depth + 1
  FROM related r
  JOIN partnership_participants pp1 ON pp1.character_id = r.id
  JOIN partnership_participants pp2
       ON pp2.partnership_id = pp1.partnership_id
      AND pp2.character_id != pp1.character_id
  WHERE r.depth < :depth  -- e.g. 1 for direct, 3 for social graph
),

-- all partnerships involving any related character
all_partnerships AS (
  SELECT DISTINCT p.*
  FROM partnerships p
  JOIN partnership_participants pp ON pp.partnership_id = p.id
  WHERE pp.character_id IN (SELECT id FROM related)
)

-- output each partnership as JSON with nested participants
SELECT
  json_object(
    'id', p.id,
    'type', p.type,
    'name', p.name,
    'participants',
      (
        SELECT json_group_array(
          json_object(
            'id', c.id,
            'name', c.name,
            'sex', c.sex,
            'role', pp.role_code
          )
        )
        FROM partnership_participants pp
        JOIN character c ON c.id = pp.character_id
        WHERE pp.partnership_id = p.id
      )
) AS partnerships_json
FROM all_partnerships p;

                """),
                {"cid": character_id, "depth": int(depth)},
            )
            .mappings()
            .all()
        )
        connections = [json.loads(row["partnerships_json"]) for row in rows]
        return connections


    @staticmethod
    def __handle_pairwise(session: Session, member1: Member, member2: Member) -> None:

        match member1.role_code:
          case (RoleCode.MATE | RoleCode.CONCUBINE | RoleCode.BETROTHED| RoleCode.PARAMOUR):
            partnership_type = Ptype.LIAISON
          case _:
            partnership_type = Ptype.FACTION
        partnership = Partnership(type=partnership_type)
        session.add(partnership)
        session.flush()  # Get the partnership ID

        participant1 = PartnershipParticipant(
            partnership_id=partnership.id,
            character_id=int(member1.character_id),
            role_code=member1.role_code,
        )
        participant2 = PartnershipParticipant(
            partnership_id=partnership.id,
            character_id=int(member2.character_id),
            role_code=member2.role_code,
        )
        session.add_all([participant1, participant2])
        session.commit()

    @staticmethod
    def __handle_association(session: Session, member: Member, association: Association) -> None:
        
        partnership = session.exec(select(Partnership).where(Partnership.name == association.name)).one_or_none()
        if not partnership:
          partnership = Partnership(type=Ptype.FACTION, name=association.name)
          session.add(partnership)
          session.flush()  

        participant = PartnershipParticipant(
            partnership_id=partnership.id,
            character_id=int(member.character_id),
            role_code=member.role_code,
        )
        session.add(participant)
        session.commit()

    @staticmethod
    def create_connection(session: Session, member1: Member, member2: Member | Association) -> None:
        """
        Create a new social connection (partnership) between two characters.

        Args:
            session: Database session
            member1: First member of the partnership
            member2: Second member of the partnership

        Returns:
            None
        """
        if isinstance(member2, Association):
            CharacterConnectionsService.__handle_association(session, member1, member2)
        else:
            CharacterConnectionsService.__handle_pairwise(session, member1, member2)
            


