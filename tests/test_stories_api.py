from charservice.modules.stories.models import Saga



class TestStoryApi:
    def test_get_permitted_story_names_by_ids(self, db_session, client):
        # Create some test data
        saga1 = Saga(title="Saga One")
        saga2 = Saga(title="Saga Two")
        db_session.add(saga1)
        db_session.add(saga2)
        db_session.commit()



        response = client.get("/api/v1/stories/get_permitted_stories_by_ids")


