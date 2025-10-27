from apifast.model import Character, Roleplaying


class TestCharacterApi:
    def test_get_characters(self, db_session, client):
        graurog = Character(
            name='Graurog',
            appearance='Female Ogrillon (Orc-Ogre)',
            background=None)
        graurog.roleplaying_attributes = [
            Roleplaying(characteristic='Blunt and direct', character=graurog),
            Roleplaying(characteristic='Loyal and protective', character=graurog),
        ]
        cinsora = Character(
            name="Cinsora",
            appearance='Dragonborne',
            background=None)
        cinsora.roleplaying_attributes = [
            Roleplaying(characteristic="Charming but unrefined", character=cinsora),
            Roleplaying(characteristic="Collects trinkets", character=cinsora)
        ]
        db_session.add_all([graurog, cinsora])
        db_session.commit()
        response = client.get("/characters")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Graurog"
        assert data[0]["appearance"] == "Female Ogrillon (Orc-Ogre)"
        assert data[0]["attributes"] == ["Blunt and direct", "Loyal and protective"]
        assert data[1]["name"] == "Cinsora"
        assert data[1]["appearance"] == "Dragonborne"
        assert data[1]["attributes"] == [
            "Charming but unrefined",
            "Collects trinkets",
        ]
