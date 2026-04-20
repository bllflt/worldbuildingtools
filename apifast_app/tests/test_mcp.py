from unittest.mock import patch

import pytest
from apifast.main import mcp
from apifast.models.enums import Ptype, RoleCode, Sex
from apifast.models.model import Character, Roleplaying
from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport


@pytest.fixture
async def main_mcp_client(db_session) -> Client[FastMCPTransport]:  #
    async with Client(mcp) as client:
        yield client


class TestMCPCharacterTools:
    async def test_mcp_characters(self, main_mcp_client: Client[FastMCPTransport]):
        with patch(
            "apifast.services.characters.CharacterService.get_character_by_id"
        ) as mock_get_character_by_id:
            mock_get_character_by_id.return_value = Character(
                id=1,
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
                name="get_character_summary", arguments={"character_id": 1}
            )
            assert result.data is not None
            assert result.structured_content == {
                "id": 1,
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
            "apifast.services.character_connections.CharacterConnectionsService.get_connections_by_character_id"
        ) as mock_get_connections:
            mock_get_connections.return_value = [
                {
                    "id": 1,
                    "type": Ptype.LIAISON,
                    "start_date": None,
                    "end_date": None,
                    "participants": [
                        {
                            "id": 1,
                            "name": "Test Character 1",
                            "role": RoleCode.MATE,
                        },
                        {
                            "id": 2,
                            "name": "Test Character 2",
                            "role": RoleCode.MATE,
                        },
                    ],
                }
            ]
            result = await main_mcp_client.call_tool(
                name="get_character_connections",
                arguments={"character_id": 1, "depth": 0},
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
                                "id": 1,
                                "name": "Test Character 1",
                                "role": RoleCode.MATE,
                            },
                            {
                                "id": 2,
                                "name": "Test Character 2",
                                "role": RoleCode.MATE,
                            },
                        ],
                    }
                ]
            }
