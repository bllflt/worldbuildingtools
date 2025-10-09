import pytest
from flaskr.model import Character, Partnership


@pytest.fixture()
def family_tree_setup(client):
    father_id = client.post("/api/v1/characters", json={
            "name": 'Father',
            "sex": Character.MALE
            }).json['id']
    mother_id = client.post("/api/v1/characters", json={
            "name": 'Mother',
            "sex": Character.FEMALE
            }).json['id']
    child1_id = client.post("/api/v1/characters", json={
            "name": 'Child1'
            }).json['id']
    child2_id = client.post("/api/v1/characters", json={
            "name": 'Child2'
            }).json['id']
    unrelated_id = client.post("/api/v1/characters", json={
            "name": 'Unrelated'
            }).json['id']
    partnership_id = client.post("/api/v1/partnerships", json={
            "type": Partnership.MARRIAGE,
            })
    client.post(f"/api/v1/partnerships/{partnership_id}/participants", json=[
            {'character_id': father_id}, {'character_id': mother_id}
            ])
 #   client.post(f"/api/v1/partnerships/{partnership_id}/offspring", json=[
  #      {'character_id': child1_id}, {'character_id': child2_id}
  #      ])
    return {
        "father_id": father_id,
        "mother_id": mother_id,
        "child1_id": child1_id,
        "child2_id": child2_id,
        "unrelated_id": unrelated_id,
        "partnership_id": partnership_id
    }


class TestFamilyTreeResource:
    def test_partnershiop(self, app_context, client):
        with app_context:

            father_id = client.post("/api/v1/characters", json={
                "name": 'Father',
                "sex": Character.MALE
                }).json['id']
            mother_id = client.post("/api/v1/characters", json={
                "name": 'Mother',
                "sex": Character.FEMALE
                }).json['id']
            partnership_id = client.post("/api/v1/partnerships", json={
                "type": Partnership.MARRIAGE}).json['id']
            resp = client.get(f'/api/v1/partnerships/{partnership_id}')
            assert resp.json == {
                    'id': 1,
                    'type': Partnership.MARRIAGE, 
                    'is_primary': False,
                    'start_date': None,
                    'end_date': None,
            }
            resp = client.post('/api/v1/partnerships/1/participants', json=[
                {"character_id": father_id},
                {"character_id": mother_id}
                ])
            resp = client.get('/api/v1/partnerships/1/participants')
            assert resp.json == [
                {'character_id': father_id, 'role': None},
                {'character_id': mother_id, 'role': None}
            ]
    
            

    def test_get_immediate_family(self, app_context, client):
        with app_context:
            father_id = client.post("/api/v1/characters", json={
                "name": 'Father',
                "sex": Character.MALE
            }).json['id']
            mother_id = client.post("/api/v1/characters", json={
                "name": 'Mother',
                "sex": Character.FEMALE
            }).json['id']
            child1_id = client.post("/api/v1/characters", json={
                "name": 'Child1'
            }).json['id']
            child2_id = client.post("/api/v1/characters", json={
                "name": 'Child2'
            }).json['id']
            unrelated_id = client.post("/api/v1/characters", json={
                "name": 'Unrelated'
            }).json['id']
            partnership_id = client.post("/api/v1/partnerships", json={
                "type": Partnership.MARRIAGE,
            }).json['id']
            client.post(f"/api/v1/partnerships/{partnership_id}/participants", json=[
                {'character_id': father_id}, {'character_id': mother_id}
            ])





            response = client.get(
                f"/api/v1/characters/{father_id}/partners"
                )
            assert response.status_code == 200
            assert response.json == [{
                'id': partnership_id,
                'partnership_type': Partnership.MARRIAGE,
                'start_date': None,
                'end_date': None,
                'is_primary': False,
                'spouses': [{
                    'id': mother_id,
                    'name': 'Mother',
                    'sex': Character.FEMALE
                }]
            }]

