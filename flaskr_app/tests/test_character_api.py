from sqlalchemy import select

from flaskr.model import Character, Image, Roleplaying, db


class TestCharacterResource:
    def test_get(self, app_context, client):
        with app_context:
            graurog = Character(name='Graurog',
                                appearance='Female Ogrillon (Orc-Ogre)',
                                background=None,
                                roleplaying=[
                                    Roleplaying(
                                        characteristic='Blunt and direct'),
                                    Roleplaying(
                                        characteristic='Loyal and protective'),
                                ])
            cinsora = Character(name="Cinsora",
                                appearance='Dragonborne',
                                background=None,
                                roleplaying=[
                                    Roleplaying(
                                        characteristic="Charming but unrefined"
                                    ),
                                    Roleplaying(
                                        characteristic="Collects trinkets"
                                    )])
            db.session.add_all([graurog, cinsora])
            db.session.commit()

            response = client.get("/api/v1/characters/1")

            assert response.status_code == 200
            assert response.json == {
                'appearance': 'Female Ogrillon (Orc-Ogre)',
                'background': None,
                'id': 1,
                'name': 'Graurog',
                'sex': 9,
                'roleplaying': [
                    'Blunt and direct',
                    'Loyal and protective'],
                'images': [],
                }

    def test_get_w_image(self, app_context, client):
        with app_context:
            graurog = Character(name='Graurog',
                                images=[
                                    Image(uri='http://moo1.png'),
                                    Image(uri='http://moo2.png')])
            db.session.add_all([graurog])
            db.session.commit()

            response = client.get("/api/v1/characters/1")
            assert response.json == {
                'appearance': None,
                'background': None,
                'id': 1,
                'sex': 9,
                'images': ['http://moo1.png', 'http://moo2.png'],
                'name': 'Graurog',
                'roleplaying': [],
            }

    def test_get_error_no_exist(self, client):
        response = client.get("/api/v1/characters/1")

        assert response.status_code == 404
        assert response.json == {
            'error': {'type': 'Not found'}}

    def test_delete(self, app_context, client):
        with app_context:
            graurog = Character(name='Graurog',
                                appearance='Female Ogrillon (Orc-Ogre)',
                                background=None,
                                roleplaying=[
                                    Roleplaying(
                                        characteristic='Blunt and direct'),
                                    Roleplaying(
                                        characteristic='Loyal and protective'),
                                ])
            cinsora = Character(name="Cinsora",
                                appearance='Dragonborne',
                                background=None,
                                roleplaying=[
                                    Roleplaying(
                                        characteristic="Charming but unrefined"
                                    ),
                                    Roleplaying(
                                        characteristic="Collects trinkets"
                                    )])
            db.session.add_all([graurog, cinsora])
            db.session.commit()

            response = client.delete('/api/v1/characters/1')
            assert response.status_code == 200

            db.session.expire_all()
            gaurog = db.session.scalar(select(Character).where(
                Character.name == 'Graurog'))
            assert gaurog is None

            roleplaying = db.session.scalars(select(Roleplaying).where(
                Roleplaying.character_id == 1)).all()
            assert roleplaying == []

    def test_delete_error_no_exist(self, client):

        response = client.delete('/api/v1/characters/1')

        assert response.status_code == 404
        assert response.json == {'error': {'type': 'Not found'}}

    def test_put(self, app_context, client):
        with app_context:
            graurog = Character(name='Fred',
                                appearance=None,
                                background=None,
                                roleplaying=[])
            cinsora = Character(name="Cinsora",
                                appearance='Dragonborne',
                                background=None,
                                roleplaying=[
                                    Roleplaying(
                                        characteristic="Charming but unrefined"
                                    ),
                                    Roleplaying(
                                        characteristic="Collects trinkets"
                                    )])
            db.session.add_all([graurog, cinsora])

            response = client.put("/api/v1/characters/1", json={
                "name": 'Graurog',
                "appearance": 'Female Ogrillon (Orc-Ogre)',
                "background": "Complex long story about the travels, ",
                "roleplaying": [
                    'Blunt and direct',
                    'Loyal and protective',
                ],
                'images': [],

            })
            assert response.status_code == 200

            db.session.expire_all()
            got = db.session.scalar(select(Character).where(
                Character.name == "Graurog"))
            assert got.background == 'Complex long story about the travels, '
            assert got.appearance == 'Female Ogrillon (Orc-Ogre)'
            assert got.roleplaying[0].characteristic == 'Blunt and direct'
            assert got.roleplaying[1].characteristic == 'Loyal and protective'

    def test_put_deletes_extra_roleplaying(self, app_context, client):
        with app_context:
            graurog = Character(
                name='Graurog',
                appearance='Female Ogrillon (Orc-Ogre)',
                background='Cheese',
                roleplaying=[
                    Roleplaying(
                        characteristic='One'),
                    Roleplaying(
                        characteristic='Two'),
                     Roleplaying(
                         characteristic='Three')
                ])
            db.session.add_all([graurog])
            db.session.commit()

            client.put('/api/v1/characters/1', json={
                "name": 'Graurog',
                "appearance": 'Female Ogrillon (Orc-Ogre)',
                "background": 'Cheese',
                "roleplaying": ['Four']
            })
            db.session.expire_all()
            graurog = db.session.scalar(select(Character).where(
                Character.name == 'Graurog'))
            assert len(graurog.roleplaying) == 1
            assert graurog.roleplaying[0].characteristic == 'Four'

    def test_put_no_exist(self, app_context, client):
        with app_context:
            response = client.put('/api/v1/characters/1', json={
                "name": 'Graurog',
                "appearance": 'Female Ogrillon (Orc-Ogre)',
                "background": 'Cheese',
                "roleplaying": ['Four']
            })
            assert response.status_code == 404
            assert response.json == {'error': {'type': 'Not found'}}

            got = db.session.scalar(select(Character).where(
                Character.name == "Graurog"))
            assert got is None
