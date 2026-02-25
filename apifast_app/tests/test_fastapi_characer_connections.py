from apifast.model import Ptype, RoleCode, Sex

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
        pid = family_tree_setup["partnership_id"]
        resp = client.get(f"/api/v1/partnerships/{pid}/participants")
        assert resp.status_code == 200
        expected = [
            {
                "character_id": family_tree_setup["father_id"],
                "role_code": RoleCode.MATE,
            },
            {
                "character_id": family_tree_setup["mother_id"],
                "role_code": RoleCode.MATE,
            },
            {
                "character_id": family_tree_setup["child1_id"],
                "role_code": RoleCode.CHILD,
            },
            {
                "character_id": family_tree_setup["child2_id"],
                "role_code": RoleCode.CHILD,
            },
        ]
        # Sort by character_id to ensure deterministic comparison
        assert sorted(resp.json(), key=lambda x: x["character_id"]) == sorted(
            expected, key=lambda x: x["character_id"]
        )

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
                        "role": RoleCode.MATE,
                    },
                    {
                        "id": family_tree_setup["mother_id"],
                        "name": "Mother",
                        "sex": int(Sex.FEMALE),
                        "role": RoleCode.MATE,
                    },
                    {
                        "id": family_tree_setup["child1_id"],
                        "name": "Child1",
                        "sex": int(Sex.UNKNOWN),
                        "role": RoleCode.CHILD,
                    },
                    {
                        "id": family_tree_setup["child2_id"],
                        "name": "Child2",
                        "sex": int(Sex.UNKNOWN),
                        "role": RoleCode.CHILD,
                    },
                ],
            }
        ]
