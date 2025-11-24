from apifast.db import get_db_context
from apifast.model import CharacterRead, CharacterWrite
from apifast.services.characters import CharacterQuery, CharacterService
from fastmcp import FastMCP

mcp = FastMCP("Character Tools")


@mcp.tool()
def get_character_id_list() -> list[tuple[str, int]]:
    """
    A list of all character names and ids.
    """
    with get_db_context() as session:
        rv = CharacterService.get_characters(
            session,
            CharacterQuery(
                fields={"id", "name"},
            ),
        )
        return [(row.name, row.id) for row in rv]


@mcp.tool()
def get_character_detail(char_id: int) -> CharacterRead:
    """
    Get the details of a character with the given ID.
    """
    with get_db_context() as session:
        char = CharacterService.get_character_by_id(session, char_id)
        return CharacterRead.model_validate(char)


@mcp.tool()
def search_character_by_name_substring(name_substring: str) -> list[tuple[str, int]]:
    """
    A list of character names and their ids that contain the given substring.
    """
    with get_db_context() as session:
        rv = CharacterService.get_characters(
            session,
            CharacterQuery(
                name=name_substring,
                fields={"id", "name"},
            ),
        )
        return [(row.name, row.id) for row in rv]


@mcp.tool()
def add_character(character: CharacterWrite) -> CharacterRead:
    """
    Add a new character.
    """
    with get_db_context() as session:
        char = CharacterService.create_character(session, character)
        return CharacterRead.model_validate(char)


@mcp.tool()
def update_character(char_id: int, character: CharacterWrite) -> None:
    """
    Updates a character. Full update (PUT). If only some fields are provided, automatically fill missing fields with the current character values to avoid data loss.
    """
    with get_db_context() as session:
        CharacterService.update_character(session, char_id, character)


@mcp.tool()
def delete_character(char_id: int) -> None:
    """
    Delete a character.
    """
    with get_db_context() as session:
        CharacterService.delete_character(session, char_id)
