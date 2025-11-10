import pytest
from apifast.model import Ptype, Role, Sex
from fastapi.testclient import TestClient


@pytest.fixture
def family_tree_setup(client: TestClient) -> dict[str, int]:
    """
    Sets up a family tree with a father, mother, two children, and one partnership.
    Returns a dictionary of the created character and partnership IDs.
    """
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
        json={"name": "Child2", "sex": Sex.UNKNOWN},
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
