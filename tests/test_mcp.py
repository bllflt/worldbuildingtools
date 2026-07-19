from unittest.mock import patch
from uuid import UUID
import pytest
from fastmcp import Client
from fastmcp.client.transports import FastMCPTransport

from charservice.main import mcp
from charservice.models.enums import Ptype, RoleCode, Sex
from charservice.models.model import Character, Roleplaying


@pytest.fixture
async def main_mcp_client(db_session) -> Client[FastMCPTransport]: #type: ignore
    async with Client(mcp) as client:
        yield client # type: ignore


@pytest.fixture(autouse=True)
def mock_get_access_token():
    with patch("charservice.mcp.characters.get_access_token") as mock:
        class MockToken:
            claims = {
                "story_uuid": "test-story",
                "permitted_stories": ["test-story"],
            }
        mock.return_value = MockToken()
        yield mock


@pytest.mark.asyncio
class TestMCPCharacterTools:
    async def test_mcp_characters(self, main_mcp_client: Client[FastMCPTransport]):
        with patch(
            "charservice.services.characters.CharacterService.get_character_by_id"
        ) as mock_get_character_by_id:
            mock_get_character_by_id.return_value = Character(
                id=UUID(int=1),
                story_uuid="test-story",
                name="Test Character",
                appearance="Test Appearance",
                background="Test Background",
                roleplaying_attributes=[
                    Roleplaying(characteristic="Test Characteristic 1"),
                    Roleplaying(characteristic="Test Characteristic 2"),
                ],
                sex=Sex.NA,
            )

            result = await main_mcp_client.call_tool(
                name="get_character_summary", arguments={"character_id": UUID(int=1)}
            )
            assert result.data is not None
            assert result.structured_content == {
                "id": "00000000-0000-0000-0000-000000000001",
                "story_uuid": "test-story",
                "name": "Test Character",
                "appearance": "Test Appearance",
                "background": "Test Background",
                "roleplaying": [
                    "Test Characteristic 1",
                    "Test Characteristic 2",
                ],
                "images": [],
                "sex": Sex.NA,
            }

    async def test_mcp_character_connections(
        self, main_mcp_client: Client[FastMCPTransport]
    ):
        with patch(
            "charservice.services.character_connections.CharacterConnectionsService.get_connections_by_character_id"
        ) as mock_get_connections:
            mock_get_connections.return_value = [
                {
                    "id": 1,
                    "type": Ptype.LIAISON,
                    "start_date": None,
                    "end_date": None,
                    "participants": [
                        {
                            "id": UUID(int=1),
                            "name": "Test Character 1",
                            "role": RoleCode.MATE,
                        },
                        {
                            "id": UUID(int=2),
                            "name": "Test Character 2",
                            "role": RoleCode.MATE,
                        },
                    ],
                }
            ]
            result = await main_mcp_client.call_tool(
                name="get_character_connections",
                arguments={"character_id": UUID(int=1), "depth": 0},
            )
            assert result.structured_content == {
                "result": [
                    {
                        "id": 1,
                        "type": Ptype.LIAISON,
                        "start_date": None,
                        "end_date": None,
                        "participants": [
                            {
                                "id": "00000000-0000-0000-0000-000000000001",
                                "name": "Test Character 1",
                                "role": RoleCode.MATE,
                            },
                            {
                                "id": "00000000-0000-0000-0000-000000000002",
                                "name": "Test Character 2",
                                "role": RoleCode.MATE,
                            },
                        ],
                    }
                ]
            }
