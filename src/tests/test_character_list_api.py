import pytest
from sqlalchemy import select

from flaskr.model import Character, Roleplaying, db


class TestCharacterListResource:

    def test_get(self, app_context, client):
        with app_context:
            graurog = Character(name='Graurog',
                                appearance='Female Ogrillon (Orc-Ogre)',
                                background=None,
                                sex=2,
                                roleplaying=[
                                    Roleplaying(
                                        characteristic='Blunt and direct'),
                                    Roleplaying(
                                        characteristic='Loyal and protective'),
                                ])
            cinsora = Character(name="Cinsora",
                                appearance='Dragonborn',
                                background=None,
                                sex=0,
                                roleplaying=[
                                    Roleplaying(
                                        characteristic="Charming but unrefined"
                                    ),
                                    Roleplaying(
                                        characteristic="Collects trinkets"
                                    )])
            db.session.add_all([graurog, cinsora])
            db.session.commit()

            got = client.get("/api/v1/characters").json

            assert got == [{
                'appearance': 'Female Ogrillon (Orc-Ogre)',
                'background': None,
                'id': 1,
                'name': 'Graurog',
                'sex': 2,
                'roleplaying': [
                    'Blunt and direct',
                    'Loyal and protective',
                    ],
                'images': [],
                }, {
                'appearance': 'Dragonborn',
                'background': None,
                'id': 2,
                'name': 'Cinsora',
                'sex': 0,
                'roleplaying': [
                   'Charming but unrefined',
                   'Collects trinkets',
                ],
                'images': [],
                }
            ]

    @pytest.mark.parametrize("attribute, expected", [
        ('name', 'Graurog'),
        ('appearance', 'Female Ogrillon (Orc-Ogre)'),
        ('background', ''),
        ])
    def test_put(self,
                 app_context, client, attribute, expected):
        response = client.post("/api/v1/characters", json={
            "name": 'Graurog',
            "appearance": 'Female Ogrillon (Orc-Ogre)',
            "background": '',
            "roleplaying": []
            })
        assert response.status_code == 200

        with app_context:
            got = db.session.scalar(select(Character).where(
                Character.name == "Graurog"))
            assert getattr(got, attribute) == expected

    def test_put_w_roleplaying(self, app_context, client):

        response = client.post("/api/v1/characters", json={
            "name": 'Graurog',
            "appearance": 'Female Ogrillon (Orc-Ogre)',
            "background": "",
            "roleplaying": [
                 'Blunt and direct',
                 'Loyal and protective',
            ]
            })
        assert response.status_code == 200

        with app_context:
            got_graurog = db.session.scalar(select(Character).where(
                Character.name == "Graurog"))

            got_rp = list()
            for rp in got_graurog.roleplaying:
                got_rp.append(rp.characteristic)

            assert got_rp == [
                'Blunt and direct',
                'Loyal and protective'
            ]

    def test_put_error(self, app_context, client):

        response = client.post("/api/v1/characters", json={
            "name": '',
            "appearance": 'Green monkey',
            "background": "Once upon a time",
            "roleplaying": [
                 'Blunt and direct',
                 'Loyal and protective',
            ]
            })
        assert response.status_code == 400
        assert response.json == {
            'error': {
                'message': {
                    'name': [
                        'Shorter than minimum length 1.',
                    ],
                },
                'type': 'validation',
            }}

    def test_get_sorted_by_name(self, app_context, client):
        with app_context:
            a = Character(name="a")
            b = Character(name="b")
            c = Character(name="c")
            db.session.add_all([c, b, a])
            db.session.commit()
            got = client.get('/api/v1/characters?sort="name"').json
            got = list(map(lambda x: x['name'], got))
            assert got == ['a', 'b', 'c']

    def test_get_by_name(self, app_context, client):
        with app_context:
            a = Character(name="a")
            b = Character(name="b")
            c = Character(name="c")
            bill = Character(name="bill")
            billy = Character(name="billy")
            ybill = Character(name="ybill")
            db.session.add_all([c, b, a, billy, bill, ybill])
            db.session.commit()
            got = client.get('/api/v1/characters?sort=name&name=bill').json
            got = list(map(lambda x: x['name'], got))
            assert got == ['bill', 'billy', 'ybill']