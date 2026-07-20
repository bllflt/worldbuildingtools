from charservice.modules.stories.models import Saga



class TestStoryApi:
    def test_get_permitted_story_names_by_ids(self, db_session, client):
        # Create some test data
        saga1 = Saga(title="Saga One")
        saga2 = Saga(title="Saga Two")
        db_session.add(saga1)
        db_session.add(saga2)
        db_session.commit()



        response = client.get(
            "/api/v1/get_permitted_stories_by_ids",
            headers={"X-Permitted-Stories": f"{saga1.id},{saga2.id}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        # Verify the returned list contains the stories with correct mapping
        items_map = {item["uuid"]: item["name"] for item in data}
        assert items_map[saga1.id] == "Saga One"
        assert items_map[saga2.id] == "Saga Two"


