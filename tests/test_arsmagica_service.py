from charservice.models.model import Character
from charservice.modules.arsmagica.models import Category, Flaw, Virtue
from charservice.modules.arsmagica.service import (
    FlawQuery,
    FlawService,
    VirtueQuery,
    VirtueService,
)


def test_virtue_and_flaw_services_share_character_trait_operations(db_session):
    category = Category(code="Hermetic")
    virtue = Virtue(
        name="Affinity with Art",
        description="Learn Art faster",
        category="Hermetic",
        level="Minor",
    )
    flaw = Flaw(
        name="Cursed",
        description="A persistent curse",
        category="Hermetic",
        level="Major",
    )
    character = Character(story_uuid="test-story", name="Test character")
    db_session.add_all([category, virtue, flaw, character])
    db_session.commit()
    assert character.id is not None

    assert VirtueService.get_virtues(db_session, VirtueQuery(name="Affinity")) == [
        virtue
    ]
    assert FlawService.get_flaws(db_session, FlawQuery(name="Cursed")) == [flaw]
    assert VirtueService.get_virtue_by_name(db_session, virtue.name) == virtue
    assert FlawService.get_flaw_by_name(db_session, flaw.name) == flaw

    VirtueService.update_virtue_of_character(db_session, character.id, virtue.name)
    FlawService.update_flaw_of_character(db_session, character.id, flaw.name)
    assert VirtueService.get_virtues_of_character(db_session, character.id) == [
        virtue.name
    ]
    assert FlawService.get_flaws_of_character(db_session, character.id) == [flaw.name]

    VirtueService.remove_virtue_of_character(db_session, character.id, virtue.name)
    FlawService.remove_flaw_of_character(db_session, character.id, flaw.name)
    assert VirtueService.get_virtues_of_character(db_session, character.id) == []
    assert FlawService.get_flaws_of_character(db_session, character.id) == []
