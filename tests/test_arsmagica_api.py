from sqlmodel import select

from charservice.models.model import Character
from charservice.modules.arsmagica.enums import AbilityTypeCode
from charservice.modules.arsmagica.models import (
    Ability,
    AbilityType,
    Category,
    CharacterXAbility,
    Flaw,
    Virtue,
)


class TestArsMagicaApiGet:
    def test_get_abilities_and_ability_details(self, db_session, client):
        ac = AbilityType(code=AbilityTypeCode.GENERAL)
        db_session.add(ac)
        db_session.commit()

        ability = Ability(
            name="Athletics",
            description="Physical exertion and movement",
            type="General",
            specialties="running, jumping",
        )
        db_session.add(ability)
        db_session.commit()

        response = client.get("/api/v1/abilities?fields=name&sort=name")
        assert response.status_code == 200
        assert response.json() == [{"name": "Athletics"}]

        response = client.get("/api/v1/abilities/Athletics")
        assert response.status_code == 200
        assert response.json() == {
            "name": "Athletics",
            "description": "Physical exertion and movement",
            "type": "General",
            "specialties": "running, jumping",
        }

    def test_character_ability_endpoints(self, db_session, client):
        character = Character(story_uuid="test-story", name="Test character")
        ac = AbilityType(code=AbilityTypeCode.GENERAL)
        db_session.add(ac)
        db_session.commit()
        ability = Ability(
            name="Athletics", description="Physical exertion", type="General"
        )
        db_session.add_all([character, ability])
        db_session.commit()

        response = client.post(
            f"/api/v1/characters/{character.id}/abilities/",
            json={
                "name": ability.name,
                "score": 3,
                "exp": 15,
                "speciality": "running",
            },
        )
        assert response.status_code == 204
        character_ability = db_session.exec(select(CharacterXAbility)).one()
        assert character_ability.score == 3
        assert character_ability.exp == 15
        assert character_ability.speciality == "running"

        response = client.get(f"/api/v1/characters/{character.id}/abilities")
        assert response.status_code == 200
        assert response.json() == ["Athletics"]

        response = client.delete(
            f"/api/v1/characters/{character.id}/abilities/{ability.name}"
        )
        assert response.status_code == 204

        response = client.get(f"/api/v1/characters/{character.id}/abilities")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_virtues(self, db_session, client):
        cat = Category(code="Hermetic")
        v1 = Virtue(
            name="Affinity with Art",
            description="Learn Art faster",
            category="Hermetic",
            level="Minor",
        )
        v2 = Virtue(
            name="Book Magic",
            description="Magic with books",
            category="Hermetic",
            level="Minor",
        )
        db_session.add_all([cat, v1, v2])
        db_session.commit()

        response = client.get("/api/v1/virtues")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_virtues_sort_and_fields(self, db_session, client):
        cat = Category(code="Hermetic")
        v1 = Virtue(
            name="Z-Virtue", description="Desc Z", category="Hermetic", level="Minor"
        )
        v2 = Virtue(
            name="A-Virtue", description="Desc A", category="Hermetic", level="Major"
        )
        db_session.add_all([cat, v1, v2])
        db_session.commit()

        response = client.get("/api/v1/virtues?fields=name&sort=name")
        assert response.status_code == 200
        data = response.json()
        assert data == [{"name": "A-Virtue"}, {"name": "Z-Virtue"}]

    def test_get_virtues_filter_name(self, db_session, client):
        cat = Category(code="Hermetic")
        v1 = Virtue(
            name="Fire Touch",
            description="Touch of fire",
            category="Hermetic",
            level="Minor",
        )
        v2 = Virtue(
            name="Ice Touch",
            description="Touch of ice",
            category="Hermetic",
            level="Minor",
        )
        db_session.add_all([cat, v1, v2])
        db_session.commit()

        response = client.get("/api/v1/virtues?name=Fire")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Fire Touch"

    def test_get_virtues_invalid_fields(self, client):
        response = client.get("/api/v1/virtues?fields=invalid_field")
        assert response.status_code == 400
        assert "Invalid fields requested" in response.json()["detail"]

    def test_get_flaws_sort_filter_and_fields(self, db_session, client):
        category = Category(code="Hermetic")
        flaw_z = Flaw(
            name="Z-Flaw",
            description="Desc Z",
            category="Hermetic",
            level="Minor",
        )
        flaw_a = Flaw(
            name="A-Flaw",
            description="Desc A",
            category="Hermetic",
            level="Major",
        )
        db_session.add_all([category, flaw_z, flaw_a])
        db_session.commit()

        response = client.get("/api/v1/flaws?name=Flaw&sort=name&fields=name")

        assert response.status_code == 200
        assert response.json() == [{"name": "A-Flaw"}, {"name": "Z-Flaw"}]

    def test_get_flaws_keyword_query_fields_and_limit(self, db_session, client):
        category = Category(code="Hermetic")
        matching_flaw = Flaw(
            name="Cursed",
            description="A persistent curse",
            category="Hermetic",
            level="Major",
        )
        other_flaw = Flaw(
            name="Disfigured",
            description="A visible mark",
            category="Hermetic",
            level="Minor",
        )
        db_session.add_all([category, matching_flaw, other_flaw])
        db_session.commit()

        response = client.get(
            "/api/v1/flaws?q=persistent+curse&mode=keyword&fields=name&limit=1"
        )

        assert response.status_code == 200
        assert response.json() == [{"name": "Cursed"}]
