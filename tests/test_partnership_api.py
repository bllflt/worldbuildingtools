from sqlmodel import select

from charservice.models.model import (
    Character,
    Partnership,
    PartnershipParticipant,
    Ptype,
)


class TestPartnershipApiGet:
    def test_get_partnerships_empty(self, client):
        """Test retrieving partnerships when none exist."""
        response = client.get("/api/v1/partnerships")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_partnerships(self, db_session, client):
        """Test retrieving all partnerships."""
        p1 = Partnership(type=Ptype.LIAISON, name=None)
        p2 = Partnership(type=Ptype.FACTION, name="The Guild")
        db_session.add_all([p1, p2])
        db_session.commit()

        response = client.get("/api/v1/partnerships")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        has_guild = any(d["name"] == "The Guild" for d in data)
        has_none = any(d["name"] is None for d in data)
        assert has_guild and has_none

    def test_get_partnerships_faction_filter(self, db_session, client):
        """Test filtering partnerships by faction type."""
        p1 = Partnership(type=Ptype.LIAISON, name=None)
        p2 = Partnership(type=Ptype.FACTION, name="The Guild")
        p3 = Partnership(type=Ptype.FACTION, name="The Order")
        db_session.add_all([p1, p2, p3])
        db_session.commit()

        response = client.get("/api/v1/partnerships?faction=true")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        names = sorted([d["name"] for d in data])
        assert names == ["The Guild", "The Order"]

    def test_get_partnership_by_id(self, db_session, client):
        """Test retrieving a specific partnership."""
        p = Partnership(type=Ptype.FACTION, name="The Guild")
        db_session.add(p)
        db_session.commit()

        response = client.get(f"/api/v1/partnerships/{p.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "The Guild"
        assert data["type"] == Ptype.FACTION
        # Note: id field is excluded in response_model

    def test_get_partnership_not_found(self, client):
        """Test 404 when partnership doesn't exist."""
        response = client.get("/api/v1/partnerships/999")
        assert response.status_code == 404


class TestPartnershipApiPost:
    def test_post_partnership(self, db_session, client):
        """Test creating a new partnership."""
        payload = {
            "type": Ptype.LIAISON,
            "name": None,
            "start_date": None,
            "end_date": None,
        }
        response = client.post("/api/v1/partnerships", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == Ptype.LIAISON
        assert data["name"] is None

        assert len(db_session.exec(select(Partnership)).all()) == 1

    def test_post_partnership_with_name(self, db_session, client):
        """Test creating a partnership with a name."""
        payload = {
            "type": Ptype.FACTION,
            "name": "The Guild",
            "start_date": None,
            "end_date": None,
        }
        response = client.post("/api/v1/partnerships", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "The Guild"


class TestPartnershipApiPut:
    def test_put_partnership(self, db_session, client):
        """Test updating an existing partnership."""
        p = Partnership(type=Ptype.LIAISON, name=None)
        db_session.add(p)
        db_session.commit()

        payload = {
            "type": Ptype.FACTION,
            "name": "Updated",
            "start_date": None,
            "end_date": None,
        }
        response = client.put(f"/api/v1/partnerships/{p.id}", json=payload)
        assert response.status_code == 204

        db_session.refresh(p)
        assert p.type == Ptype.FACTION
        assert p.name == "Updated"

    def test_put_partnership_not_found(self, client):
        """Test updating non-existent partnership."""
        payload = {
            "type": Ptype.LIAISON,
            "name": None,
            "start_date": None,
            "end_date": None,
        }
        response = client.put("/api/v1/partnerships/999", json=payload)
        assert response.status_code == 404


class TestPartnershipApiDelete:
    def test_delete_partnership(self, db_session, client):
        """Test deleting a partnership."""
        p = Partnership(type=Ptype.LIAISON, name=None)
        db_session.add(p)
        db_session.commit()
        pid = p.id

        response = client.delete(f"/api/v1/partnerships/{pid}")
        assert response.status_code == 204

        assert db_session.get(Partnership, pid) is None

    def test_delete_not_found(self, client):
        """Test deleting non-existent partnership."""
        response = client.delete("/api/v1/partnerships/999")
        assert response.status_code == 404


class TestPartnershipParticipantApiGet:
    def test_get_participants_empty(self, db_session, client):
        """Test retrieving participants when none exist."""
        p = Partnership(type=Ptype.LIAISON, name=None)
        db_session.add(p)
        db_session.commit()

        response = client.get(f"/api/v1/partnerships/{p.id}/participants")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_participants(self, db_session, client):
        """Test retrieving all participants in a partnership."""
        c1 = Character(story_uuid="test-story", name="Character 1")
        c2 = Character(story_uuid="test-story", name="Character 2")
        p = Partnership(type=Ptype.LIAISON, name=None)
        db_session.add_all([c1, c2, p])
        db_session.commit()

        pp1 = PartnershipParticipant(
            partnership_id=p.id, character_id=c1.id, role_code="FRIEND"
        )
        pp2 = PartnershipParticipant(
            partnership_id=p.id, character_id=c2.id, role_code="MENTOR"
        )
        db_session.add_all([pp1, pp2])
        db_session.commit()

        response = client.get(f"/api/v1/partnerships/{p.id}/participants")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_participants_partnership_not_found(self, client):
        """Test 404 when partnership doesn't exist."""
        response = client.get("/api/v1/partnerships/999/participants")
        assert response.status_code == 404

    def test_get_participant_by_ids(self, db_session, client):
        """Test retrieving a specific participant."""
        c = Character(story_uuid="test-story", name="Character")
        p = Partnership(type=Ptype.LIAISON, name=None)
        db_session.add_all([c, p])
        db_session.commit()

        pp = PartnershipParticipant(
            partnership_id=p.id, character_id=c.id, role_code="FRIEND"
        )
        db_session.add(pp)
        db_session.commit()

        response = client.get(f"/api/v1/partnerships/{p.id}/participants/{c.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["role_code"] == "FRIEND"

    def test_get_participant_not_found(self, client):
        """Test 404 when participant doesn't exist."""
        response = client.get("/api/v1/partnerships/1/participants/1")
        assert response.status_code == 404


class TestPartnershipParticipantApiPost:
    def test_add_participants(self, db_session, client):
        """Test adding participants to a partnership."""
        c1 = Character(story_uuid="test-story", name="Character 1")
        c2 = Character(story_uuid="test-story", name="Character 2")
        p = Partnership(type=Ptype.LIAISON, name=None)
        db_session.add_all([c1, c2, p])
        db_session.commit()

        payload = [
            {"character_id": c1.id, "role_code": "FRIEND"},
            {"character_id": c2.id, "role_code": "MENTOR"},
        ]
        response = client.post(
            f"/api/v1/partnerships/{p.id}/participants", json=payload
        )
        assert response.status_code == 204

        participants = db_session.exec(
            select(PartnershipParticipant).where(
                PartnershipParticipant.partnership_id == p.id
            )
        ).all()
        assert len(participants) == 2

    def test_add_participants_partnership_not_found(self, client):
        """Test error when partnership doesn't exist."""
        payload = [{"character_id": 1, "role_code": "FRIEND"}]
        response = client.post("/api/v1/partnerships/999/participants", json=payload)
        assert response.status_code == 404

    def test_add_participants_character_not_found(self, db_session, client):
        """Test error when character doesn't exist."""
        p = Partnership(type=Ptype.LIAISON, name=None)
        db_session.add(p)
        db_session.commit()

        payload = [{"character_id": 999, "role_code": "FRIEND"}]
        response = client.post(
            f"/api/v1/partnerships/{p.id}/participants", json=payload
        )
        assert response.status_code == 404


class TestPartnershipParticipantApiPut:
    def test_update_participant(self, db_session, client):
        """Test updating participant role."""
        c = Character(story_uuid="test-story", name="Character")
        p = Partnership(type=Ptype.LIAISON, name=None)
        db_session.add_all([c, p])
        db_session.commit()

        pp = PartnershipParticipant(
            partnership_id=p.id, character_id=c.id, role_code="FRIEND"
        )
        db_session.add(pp)
        db_session.commit()

        payload = {"character_id": c.id, "role_code": "MENTOR"}
        response = client.put(
            f"/api/v1/partnerships/{p.id}/participants/{c.id}", json=payload
        )
        assert response.status_code == 204

        db_session.refresh(pp)
        assert pp.role_code == "MENTOR"

    def test_update_participant_not_found(self, client):
        """Test error when participant doesn't exist."""
        payload = {"character_id": 1, "role_code": "MENTOR"}
        response = client.put("/api/v1/partnerships/1/participants/1", json=payload)
        assert response.status_code == 404


class TestPartnershipParticipantApiDelete:
    def test_delete_participant(self, db_session, client):
        """Test removing a participant."""
        c = Character(story_uuid="test-story", name="Character")
        p = Partnership(type=Ptype.LIAISON, name=None)
        db_session.add_all([c, p])
        db_session.commit()

        pp = PartnershipParticipant(
            partnership_id=p.id, character_id=c.id, role_code="FRIEND"
        )
        db_session.add(pp)
        db_session.commit()

        response = client.delete(f"/api/v1/partnerships/{p.id}/participants/{c.id}")
        assert response.status_code == 204

        remaining = db_session.exec(
            select(PartnershipParticipant).where(
                PartnershipParticipant.partnership_id == p.id,
                PartnershipParticipant.character_id == c.id,
            )
        ).all()
        assert len(remaining) == 0

    def test_delete_participant_not_found(self, client):
        """Test error when participant doesn't exist."""
        response = client.delete("/api/v1/partnerships/1/participants/1")
        assert response.status_code == 404
