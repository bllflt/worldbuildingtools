from apifast.model import Character, Image, Roleplaying
from sqlmodel import select


class TestCharacterApi:
    def test_get_characters(self, db_session, client):
        graurog = Character(
            name='Graurog',
            appearance='Female Ogrillon (Orc-Ogre)',
            background=None,
            roleplaying_attributes=[
                Roleplaying(characteristic='Blunt and direct'),
                Roleplaying(characteristic='Loyal and protective'),
            ])
        
        cinsora = Character(
            name="Cinsora",
            appearance='Dragonborne',
            background=None,
            roleplaying_attributes=[
                 Roleplaying(characteristic="Charming but unrefined"),
                 Roleplaying(characteristic="Collects trinkets")
            ])

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
                "attributes": ["Charming but unrefined", "Collects trinkets"],
                "sex": 9,
                "images": []
            },
            {
                "name": "Graurog",
                "background": None,
                "appearance": "Female Ogrillon (Orc-Ogre)",
                "attributes": ["Blunt and direct", "Loyal and protective"],
                "sex": 9,
                "images": []
            },
        ]
        assert sorted_data == expected_data

    def test_get_w_image(self, db_session, client):
        
        graurog = Character(
            name='Graurog',
            appearance=None,
            background=None)
        graurog.image_attributes = [
            Image(uri='http://moo1.png'),
            Image(uri='http://moo2.png')
        ]

        db_session.add_all([graurog])
        db_session.commit()

        response = client.get("/api/v1/characters/1")
        assert response.json() == {
                'appearance': None,
                'background': None,
                'id': 1,
                'sex': 9,
                'attributes': [],
                'images': ['http://moo1.png', 'http://moo2.png'],
                'name': 'Graurog',
            }
        
    def test_get_error_no_exist(self, client):

        response = client.get("/api/v1/characters/1")

        assert response.status_code == 404
        assert response.json() == {'detail': 'Character with id 1 not found'}

    def test_delete(self, db_session, client):

      graurog = Character(name='Graurog',
                          appearance='Female Ogrillon (Orc-Ogre)',
                          background=None,
                          roleplaying_attributes=[
                              Roleplaying(
                                  characteristic='Blunt and direct'),
                              Roleplaying(
                                    characteristic='Loyal and protective'),
                            ])
      cinsora = Character(name="Cinsora",
                          appearance='Dragonborne',
                          background=None,
                          roleplaying_attributes=[
                              Roleplaying(characteristic="Charming but unrefined"),
                              Roleplaying(characteristic="Collects trinkets")
                            ])
      db_session.add_all([graurog, cinsora])
      db_session.commit()

      response = client.delete('/api/v1/characters/1')
      assert response.status_code == 204

      db_session.expire_all()
      gaurog = db_session.exec(select(Character).where(Character.name == 'Graurog')).first()
      assert gaurog is None

      roleplaying = db_session.exec(select(Roleplaying).where(Roleplaying.character_id == 1)).all()
      assert roleplaying == []

    def test_delete_not_found(self, client):
        response = client.delete("/api/v1/characters/999")
        assert response.status_code == 404
        assert response.json() == {'detail': 'Character with id 999 not found'}