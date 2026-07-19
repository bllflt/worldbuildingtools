from uuid import UUID

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_access_token

from charservice.db import get_db_context
from charservice.models.schemas import CharacterReadMCP, CharacterWrite
from charservice.services.characters import CharacterQuery, CharacterService

mcp = FastMCP("Character Tools")


@mcp.tool()
def get_character_id_list() -> list[tuple[str, int]]:
    """
    A list of all character names and ids.
    """
    token = get_access_token()
    if not token:
        return []
    with get_db_context() as session:
        rv = CharacterService.get_characters(
            session,
            CharacterQuery(
                story_uuid=token.claims.get("story_uuid"),
                fields={"id", "name"},
            ),
        )
        return [(row.name, row.id) for row in rv]


@mcp.tool()
def get_character_summary(
    character_id: UUID,
) -> CharacterReadMCP:
    """
    Get the general summary of a character with the given ID.
    """
    token = get_access_token()
    with get_db_context() as session:
        char = CharacterService.get_character_by_id(
            session,
            character_id,
            permitted_stories=token.claims.get("permitted_stories"),
        )
        return CharacterReadMCP.model_validate(char)


@mcp.tool()
def search_character_by_name_substring(name_substring: str) -> list[tuple[str, int]]:
    """
    A list of character names and their ids that contain the given substring.
    """
    token = get_access_token()
    with get_db_context() as session:
        rv = CharacterService.get_characters(
            session,
            CharacterQuery(
                story_uuid=token.claims.get("story_uuid"),
                name=name_substring,
                fields={"id", "name"},
            ),
        )
        return [(row.name, row.id) for row in rv]


@mcp.tool()
def add_character(character: CharacterWrite) -> CharacterReadMCP:
    """
    Add a new character.
    """
    token = get_access_token()
    with get_db_context() as session:
        char = CharacterService.create_character(
            session, story_uuid=token.claims.get("story_uuid"), character=character
        )
        return CharacterReadMCP.model_validate(char)


@mcp.tool()
def update_character(char_id: UUID, character: CharacterWrite) -> None:
    """
    Updates a character. You must adopt full-resource replacement semantics.
    Constraint: You must resubmit all fields from the original object, even if they remain unchanged.
    Do not assume fields are preserved if omitted.
    """
    token = get_access_token()
    with get_db_context() as session:
        CharacterService.update_character(
            session,
            char_id,
            character,
            permitted_stories=[token.claims.get("story_uuid")],
        )


@mcp.tool()
def delete_character(char_id: UUID) -> None:
    """
    Delete a character.
    """
    token = get_access_token()
    with get_db_context() as session:
        CharacterService.delete_character(
            session, char_id, permitted_stories=[token.claims.get("story_uuid")]
        )
