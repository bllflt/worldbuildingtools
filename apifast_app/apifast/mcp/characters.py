from apifast.db import get_db
from apifast.model import CharacterRead
from apifast.services.characters import CharacterQuery, CharacterService
from fastmcp import FastMCP

mcp = FastMCP("Character Tools")


@mcp.tool()
def get_character_id_list() -> list[tuple[str, int]]:
    """
    A list of character names and ids.
    """
    with get_db() as session:
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
    with get_db() as session:
        char = CharacterService.get_character_by_id(session, char_id)
        return CharacterRead.model_validate(char)


@mcp.tool()
def search_character_by_name_substring(name_substring: str) -> list[tuple[str, int]]:
    """
    Search for characters by name substring.
    """
    with get_db() as session:
        rv = CharacterService.get_characters(
            session,
            CharacterQuery(
                name=name_substring,
                fields={"id", "name"},
            ),
        )
        return [(row.name, row.id) for row in rv]
