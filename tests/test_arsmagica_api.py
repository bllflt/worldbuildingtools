from charservice.modules.arsmagica.models import Category, Flaw, Virtue


class TestArsMagicaApiGet:
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
