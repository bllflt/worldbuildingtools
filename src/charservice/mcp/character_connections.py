from typing import List, Sequence

from fastmcp import FastMCP
from pydantic import Field

from charservice.db import get_db_context
from charservice.models.enums import RoleCode
from charservice.models.model import Character, Partnership, SocialConnection
from charservice.services.character_connections import CharacterConnectionsService
from charservice.services.partnership_participants import PartnershipParticipantService
from charservice.services.partnerships import PartnershipQuery, PartnershipService

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
    src_character_id: int = Field(description="Source character ID"),
    role: RoleCode = Field(description="Role of the first character in the connection"),
    target_character_id: int = Field(description="Target character ID"),
) -> None:
    """
    Create a bidirection connection between the source character id and target character id with the specified role. The inverse role will be automatically assigned to the target character.
    """
    with get_db_context() as session:
        CharacterConnectionsService.create_pairwise_connection(
            session, src_character_id, role, target_character_id
        )


@mcp.tool()
def get_factions_list() -> List[Partnership]:
    """Get a list of all factions."""
    with get_db_context() as session:
        return PartnershipService.get_partnerships(
            session, PartnershipQuery(faction_only=True)
        )


@mcp.tool()
def get_faction_members(
    faction_id: int = Field(description="ID of the faction to get members for"),
) -> Sequence[Character]:
    """Get a list of character IDs that are members of a faction."""
    with get_db_context() as session:
        return PartnershipParticipantService.get_characters_of_faction(
            session, faction_id
        )


@mcp.tool()
def create_faction_connection(
    character_id: int = Field(description="Character ID to add to faction"),
    faction_id: int = Field(description="Faction ID to join"),
) -> None:
    with get_db_context() as session:
        CharacterConnectionsService.create_faction_connection(
            session, character_id, faction_id
        )
