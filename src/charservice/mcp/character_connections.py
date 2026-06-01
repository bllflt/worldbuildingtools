from typing import List

from fastmcp import FastMCP
from pydantic import Field

from charservice.db import get_db_context
from charservice.models.model import SocialConnection
from charservice.modules.social.schemas import Association, Member
from charservice.services.character_connections import CharacterConnectionsService

mcp = FastMCP("Character Connections Tools")


@mcp.tool()
def get_character_connections(
    character_id: int = Field(
        description="The ID of the character to get connections for"
    ),
    depth: int = Field(
        description="Degree of social graph to return", ge=0, le=3, default=0
    ),
) -> List[SocialConnection]:
    """
    Get social connections for a character by ID and depth.

    Args:
        character_id: The ID of the character to get connections for
        depth: Degree of social graph to return (0-3). 0 for direct connections only.

    Returns:
        List of social connections (liaisons and factions) involving the character and related characters up to the specified depth.
    """
    with get_db_context() as session:
        return CharacterConnectionsService.get_connections_by_character_id(
            session, character_id, depth
        )


@mcp.tool()
def create_character_connection(
    member1: Member = Field(description="First character and role"),
    member2: Member | Association = Field(
        description="Second character and role, or association"
    ),
) -> None:
    """
    Create a social connection between two characters or a character and an association.

    Args:
        member1: The first member (character and role)
        member2: The second member (character and role, or association)
    """
    with get_db_context() as session:
        CharacterConnectionsService.create_connection(session, member1, member2)
