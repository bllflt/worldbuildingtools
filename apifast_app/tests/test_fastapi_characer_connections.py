import pytest
from apifast.model import Ptype, Role, Sex


def family_tree_setup(client) -> dict[str, int]:
    father_id = client.post(
        "/api/v1/characters", json={"name": "Father", "sex": Sex.MALE}
    ).json()["id"]
    mother_id = client.post(
        "/api/v1/characters", json={"name": "Mother", "sex": Sex.FEMALE}
    ).json()["id"]
    child1_id = client.post(
        "/api/v1/characters", json={"name": "Child1", "sex": Sex.UNKNOWN}
    ).json()["id"]
    child2_id = client.post(
        "/api/v1/characters",
        json={
            "name": "Child2",
            "sex": Sex.UNKNOWN,
        },
    ).json()["id"]
    unrelated_id = client.post("/api/v1/characters", json={"name": "Unrelated"}).json()[
        "id"
    ]
    partnership_id = client.post(
        "/api/v1/partnerships",
        json={"type": Ptype.LIAISON, "is_primary": True, "legitimate": True},
    ).json()["id"]
    client.post(
        f"/api/v1/partnerships/{partnership_id}/participants",
        json=[
            {"character_id": father_id, "role": Role.MATE},
            {"character_id": mother_id, "role": Role.MATE},
            {"character_id": child1_id, "role": Role.CHILD},
            {"character_id": child2_id, "role": Role.CHILD},
        ],
    )
    return {
        "father_id": father_id,
        "mother_id": mother_id,
        "child1_id": child1_id,
        "child2_id": child2_id,
        "unrelated_id": unrelated_id,
        "partnership_id": partnership_id,
    }


class TestCharacterConnections:
    def test_partnership(self, client):
        ts = family_tree_setup(client)

        resp = client.get(f"/api/v1/partnerships/{ts['partnership_id']}")
        assert resp.status_code == 200
        assert resp.json() == {
            "id": ts["partnership_id"],
            "type": Ptype.LIAISON,
            "is_primary": True,
            "legitimate": True,
            "start_date": None,
            "end_date": None,
            "name": None,
        }

    def test_partnership_particiants(self, client):
        ts = family_tree_setup(client)
        resp = client.get("/api/v1/partnerships/1/participants")
        assert resp.status_code == 200
        assert resp.json() == [
            {"character_id": ts["father_id"], "role": Role.MATE},
            {"character_id": ts["mother_id"], "role": Role.MATE},
            {"character_id": ts["child1_id"], "role": Role.CHILD},
            {"character_id": ts["child2_id"], "role": Role.CHILD},
        ]

    def test_character_degree_connections(self, client):
        ts = family_tree_setup(client)
        response = client.get(
            f"/api/v1/characters/{ts['father_id']}/connections?degree=1"
        )
        items = response.json()
        assert items == [
            {
                "type": int(Ptype.LIAISON),
                "is_primary": True,
                "legitimate": True,
                "start_date": None,
                "end_date": None,
                "participants": [
                    {
                        "id": ts["father_id"],
                        "name": "Father",
                        "sex": int(Sex.MALE),
                        "role": int(Role.MATE),
                    },
                    {
                        "id": ts["mother_id"],
                        "name": "Mother",
                        "sex": int(Sex.FEMALE),
                        "role": int(Role.MATE),
                    },
                    {
                        "id": ts["child1_id"],
                        "name": "Child1",
                        "sex": int(Sex.UNKNOWN),
                        "role": int(Role.CHILD),
                    },
                    {
                        "id": ts["child2_id"],
                        "name": "Child2",
                        "sex": int(Sex.UNKNOWN),
                        "role": int(Role.CHILD),
                    },
                ],
            }
        ]
