from apifast.model import Ptype, Role, Sex

pytest_plugins = ("tests.conftest_char_connections",)


class TestCharacterConnections:
    def test_partnership(self, client, family_tree_setup):
        resp = client.get(f"/api/v1/partnerships/{family_tree_setup['partnership_id']}")
        assert resp.status_code == 200
        assert resp.json() == {
            "type": int(Ptype.LIAISON),
            "is_primary": True,
            "legitimate": True,
            "start_date": None,
            "end_date": None,
            "name": None,
        }

    def test_partnership_particiants(self, client, family_tree_setup):
        resp = client.get("/api/v1/partnerships/1/participants")
        assert resp.status_code == 200
        assert resp.json() == [
            {"character_id": family_tree_setup["father_id"], "role": Role.MATE},
            {"character_id": family_tree_setup["mother_id"], "role": Role.MATE},
            {"character_id": family_tree_setup["child1_id"], "role": Role.CHILD},
            {"character_id": family_tree_setup["child2_id"], "role": Role.CHILD},
        ]

    def test_character_degree_connections(self, client, family_tree_setup):
        response = client.get(
            f"/api/v1/characters/{family_tree_setup['father_id']}/connections?degree=1"
        )
        assert response.status_code == 200
        items = response.json()
        assert items == [
            {
                "id": family_tree_setup["partnership_id"],
                "type": int(Ptype.LIAISON),
                "is_primary": True,
                "legitimate": True,
                "start_date": None,
                "end_date": None,
                "participants": [
                    {
                        "id": family_tree_setup["father_id"],
                        "name": "Father",
                        "sex": int(Sex.MALE),
                        "role": int(Role.MATE),
                    },
                    {
                        "id": family_tree_setup["mother_id"],
                        "name": "Mother",
                        "sex": int(Sex.FEMALE),
                        "role": int(Role.MATE),
                    },
                    {
                        "id": family_tree_setup["child1_id"],
                        "name": "Child1",
                        "sex": int(Sex.UNKNOWN),
                        "role": int(Role.CHILD),
                    },
                    {
                        "id": family_tree_setup["child2_id"],
                        "name": "Child2",
                        "sex": int(Sex.UNKNOWN),
                        "role": int(Role.CHILD),
                    },
                ],
            }
        ]
