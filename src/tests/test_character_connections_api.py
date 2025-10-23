import pytest

from flaskr.model import Character, Partnership


class TestFamilyTreeResource:
    def family_tree_setup(self, client):
        father_id = client.post("/api/v1/characters", json={
            "name": 'Father',
            "sex": Character.MALE
            }).json['id']
        mother_id = client.post("/api/v1/characters", json={
            "name": 'Mother',
            "sex": Character.FEMALE
            }).json['id']
        child1_id = client.post("/api/v1/characters", json={
            "name": 'Child1',
            "sex": Character.UNKNOWN
            }).json['id']
        child2_id = client.post("/api/v1/characters", json={
            "name": 'Child2',
            "sex": Character.UNKNOWN,
            }).json['id']
        unrelated_id = client.post("/api/v1/characters", json={
            "name": 'Unrelated'
            }).json['id']
        partnership_id = client.post("/api/v1/partnerships", json={
            "type": Partnership.MARRIAGE,
            }).json['id']
        client.post(
                f"/api/v1/partnerships/{partnership_id}/participants",
                json=[{'character_id': father_id}, {'character_id': mother_id}])
        client.put(
            f"/api/v1/partnerships/{partnership_id}/offspring/{child1_id}",
            json={})
        client.put(
            f"/api/v1/partnerships/{partnership_id}/offspring/{child2_id}",
            json={})
        return {
            "father_id": father_id,
            "mother_id": mother_id,
            "child1_id": child1_id,
            "child2_id": child2_id,
            "unrelated_id": unrelated_id,
            "partnership_id": partnership_id
        }

    def test_partnership(self, app_context, client):
        with app_context:
            ts = self.family_tree_setup(client)
            resp = client.get(f'/api/v1/partnerships/{ts['partnership_id']}')
            assert resp.status_code == 200
            assert resp.json == {
                    'id': ts['partnership_id'],
                    'type': Partnership.MARRIAGE,
                    'is_primary': False,
                    'start_date': None,
                    'end_date': None,
            }

    def test_partnership_particiants(self, app_context, client):
        with app_context:
            ts = self.family_tree_setup(client)
            resp = client.get('/api/v1/partnerships/1/participants')
            assert resp.status_code == 200
            assert resp.json == [
                {'character_id': ts['father_id'], 'role': None},
                {'character_id': ts['mother_id'], 'role': None}
            ]

    def test_partnerships_offspring(self, app_context, client):
        with app_context:
            ts = self.family_tree_setup(client)
            response = client.put(
                f"/api/v1/partnerships/{ts['partnership_id']}/offspring/{ts['unrelated_id']}")
            assert response.status_code == 200
            response = client.get(
                f"/api/v1/partnerships/{ts['partnership_id']}/offspring")
            assert response.json == [
                {'character_id': ts['child1_id']},
                {'character_id': ts['child2_id']},
                {'character_id': ts['unrelated_id']}
            ]

    def test_character_degree_connections(self, app_context, client):
        with app_context:
            ts = self.family_tree_setup(client)
            response = client.get(
                f"/api/v1/characters/{ts['father_id']}/connections?degree=1"
            )
            items = response.json
            assert items == [
                { 'type': Partnership.MARRIAGE, 'id': ts["partnership_id"],
                   'participants': [
                       {'id': ts['father_id'], 'name': 'Father', 'sex': Character.MALE},      
                       {'id': ts['mother_id'], 'name': 'Mother', 'sex': Character.FEMALE}],
                   'children': [
                       {'id': ts['child1_id'], 'name': 'Child1', 'sex': Character.UNKNOWN},
                       {'id': ts['child2_id'], 'name': 'Child2', 'sex': Character.UNKNOWN}
                   ]
                }
            ]   