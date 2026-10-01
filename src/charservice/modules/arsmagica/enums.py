from enum import StrEnum


class VirtueFlawLevelCode(StrEnum):
    MAJOR = 'Major'
    MINOR = 'Minor'
    FREE = 'Free'

class CategoryCode(StrEnum):
    ANIMALS_ONLY = "animals only"
    GENERAL = "General"
    HERMETIC = "Hermetic"
    SUPERNATURAL = "Supernatural"
    PERSONALITY = "Personality"
    SOCIAL_STATUS = "Social Status"
    STORY = "Story"
    MYTHIC_COMPANION = "Mythic Companion"
    SPECIAL = "Special"
