from flaskr.model import Character, Roleplaying, db
from sqlalchemy import select
import pytest


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
                'roleplaying': [
                    'Blunt and direct',
                    'Loyal and protective']
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
