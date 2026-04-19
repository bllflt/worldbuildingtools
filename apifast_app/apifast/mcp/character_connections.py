from typing import List

from apifast.db import get_db_context
from apifast.models.model import SocialConnection
from apifast.services.character_connections import CharacterConnectionsService
from fastmcp import FastMCP
from pydantic import Field

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
