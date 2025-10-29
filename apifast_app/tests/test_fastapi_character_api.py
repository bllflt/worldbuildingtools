from apifast.model import Character, Image, Roleplaying
from sqlmodel import select


class TestCharacterApi:
    def test_get_characters(self, db_session, client):
        graurog = Character(
            name="Graurog",
            appearance="Female Ogrillon (Orc-Ogre)",
            background=None,
            roleplaying_attributes=[
                Roleplaying(characteristic="Blunt and direct"),
                Roleplaying(characteristic="Loyal and protective"),
            ],
        )

        cinsora = Character(
            name="Cinsora",
            appearance="Dragonborne",
            background=None,
            roleplaying_attributes=[
                Roleplaying(characteristic="Charming but unrefined"),
                Roleplaying(characteristic="Collects trinkets"),
            ],
        )

        db_session.add_all([graurog, cinsora])
        db_session.commit()
        response = client.get("/api/v1/characters")

        assert response.status_code == 200
        data = response.json()

        for d in data:
            d.pop("id", None)
        sorted_data = sorted(data, key=lambda x: x["name"])

        expected_data = [
            {
                "name": "Cinsora",
                "background": None,
                "appearance": "Dragonborne",
                "roleplaying": ["Charming but unrefined", "Collects trinkets"],
                "sex": 9,
                "images": [],
            },
            {
                "name": "Graurog",
                "background": None,
                "appearance": "Female Ogrillon (Orc-Ogre)",
                "roleplaying": ["Blunt and direct", "Loyal and protective"],
                "sex": 9,
                "images": [],
            },
        ]
        assert sorted_data == expected_data

    def test_post_character(self, db_session, client):
        response = client.post(
            "/api/v1/characters",
            json={
                "name": "Graurog",
                "appearance": "Female Ogrillon (Orc-Ogre)",
                "background": "",
                "roleplaying": [],
            },
        )
        assert response.status_code == 201
        assert response.json() == {
            "id": 1,
            "name": "Graurog",
            "appearance": "Female Ogrillon (Orc-Ogre)",
            "background": "",
            "roleplaying": [],
            "images": [],
            "sex": 9,
        }
        got = db_session.exec(
            (select(Character).where(Character.name == "Graurog"))
        ).one()
        assert got is not None

    def test_put_character(self, db_session, client):
        client.post(
            "/api/v1/characters",
            json={
                "name": "Graurogo",
                "appearance": "Female Ogrillon (Orc-Ogre)",
                "background": "",
                "roleplaying": [],
            },
        )
        response = client.put(
            "/api/v1/characters/1",
            json={
                "name": "Graurog",
                "appearance": "Female Ogrillon (Orc-Ogre)",
                "background": "",
                "roleplaying": [],
            },
        )

        assert response.status_code == 204

        got = db_session.exec(
            (select(Character).where(Character.name == "Graurog"))
        ).one()
        assert got is not None

    def test_put_w_roleplaying_images(self, db_session, client):
        response = client.post(
            "/api/v1/characters",
            json={
                "name": "Graurog",
                "roleplaying": [
                    "Blunt and direct",
                    "Loyal and protective",
                ],
                "images": [
                    "moo1.png",
                    "moo2.png",
                ],
            },
        )
        new_id = response.json()["id"]
        response = client.put(
            f"/api/v1/characters/{new_id}",
            json={
                "name": "Graurog",
                "roleplaying": ["Likes cheeese"],
                "images": [
                    "123434556.png",
                ],
            },
        )
        got = db_session.exec(
            (select(Character).where(Character.name == "Graurog"))
        ).one()
        assert [r.characteristic for r in got.roleplaying_attributes] == [
            "Likes cheeese"
        ]
        assert [i.uri for i in got.image_attributes] == ["123434556.png"]
        assert (
            db_session.exec((select(Image).where(Image.uri == "moo1.png")))
            .one()
            .character_id
            is None
        )

    def test_get_w_image(self, db_session, client):
        graurog = Character(name="Graurog", appearance=None, background=None)
        graurog.image_attributes = [
            Image(uri="moo1.png"),
            Image(uri="moo2.png"),
        ]

        db_session.add_all([graurog])
        db_session.commit()

        response = client.get("/api/v1/characters/1")
        assert response.json() == {
            "appearance": None,
            "background": None,
            "id": 1,
            "sex": 9,
            "roleplaying": [],
            "images": ["moo1.png", "moo2.png"],
            "name": "Graurog",
        }

    def test_get_error_no_exist(self, client):
        response = client.get("/api/v1/characters/1")

        assert response.status_code == 404
        assert response.json() == {"detail": "Character with id 1 not found"}

    def test_delete(self, db_session, client):
        graurog = Character(
            name="Graurog",
            appearance="Female Ogrillon (Orc-Ogre)",
            background=None,
            roleplaying_attributes=[
                Roleplaying(characteristic="Blunt and direct"),
                Roleplaying(characteristic="Loyal and protective"),
            ],
        )
        cinsora = Character(
            name="Cinsora",
            appearance="Dragonborne",
            background=None,
            roleplaying_attributes=[
                Roleplaying(characteristic="Charming but unrefined"),
                Roleplaying(characteristic="Collects trinkets"),
            ],
        )
        db_session.add_all([graurog, cinsora])
        db_session.commit()

        response = client.delete("/api/v1/characters/1")
        assert response.status_code == 204

        db_session.expire_all()
        gaurog = db_session.exec(
            select(Character).where(Character.name == "Graurog")
        ).first()
        assert gaurog is None

        roleplaying = db_session.exec(
            select(Roleplaying).where(Roleplaying.character_id == 1)
        ).all()
        assert roleplaying == []

    def test_delete_not_found(self, client):
        response = client.delete("/api/v1/characters/999")
        assert response.status_code == 404
        assert response.json() == {"detail": "Character with id 999 not found"}
