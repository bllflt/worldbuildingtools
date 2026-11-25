from typing import Any

from pydantic import AliasChoices, BaseModel, Field

from charservice.modules.arsmagica.enums import (
    AbilityTypeCode,
    CategoryCode,
    VirtueFlawLevelCode,
)


class VirtueFlawBaseSchema(BaseModel):
    model_config = {
        "from_attributes": True,
    }

    name: str = Field(..., description="Name of the virtue/flaw", min_length=1)
    description: str = Field(
        ..., description="Description of the virtue/flaw", min_length=1
    )
    category: CategoryCode = Field(..., description="Category of the virtue/flaw")
    level: VirtueFlawLevelCode = Field(..., description="Level of the virtue/flaw")


class VirtueSchema(VirtueFlawBaseSchema):
    tainted: bool = Field(False, description="Whether the virtue is tainted")


class FlawSchema(VirtueFlawBaseSchema):
    pass


class CharacterVirtueSchema(BaseModel):
    model_config = {
        "from_attributes": True,
    }

    name: str = Field(
        ...,
        description="Name of the virtue",
        validation_alias=AliasChoices("name", "virtue"),
    )


class CharacterFlawSchema(BaseModel):
    model_config = {
        "from_attributes": True,
    }

    name: str = Field(
        ...,
        description="Name of the flaw",
        validation_alias=AliasChoices("name", "flaw"),
    )


class AbilitySchema(BaseModel):
    model_config = {
        "from_attributes": True,
    }

    name: str = Field(..., description="Name of the ability", min_length=1)
    description: str = Field(
        ..., description="Description of the ability", min_length=1
    )
    type: AbilityTypeCode | None = Field(None, description="Type of the ability")
    specialties: str | None = Field(None, description="Specialties for the ability")
    display_template: str | None = Field(
        None, description="Template for displaying the ability"
    )


class CharacterAbilitySchema(BaseModel):
    model_config = {
        "from_attributes": True,
    }

    name: str = Field(
        ...,
        description="Name of the ability",
        validation_alias=AliasChoices("name", "ability"),
    )
    speciality: str | None = Field(default=None)
    exp: int | None = Field(default=None)
    score: int | None = Field(default=None)
    parameters: dict[str, Any] = Field(default_factory=dict, exclude=True)
    display_value: str | None = Field(default=None)


class Characteristics(BaseModel):
    model_config = {
        "from_attributes": True,
    }

    intelligence: int = Field(default=0, ge=-5, le=5)
    perception: int = Field(default=0, ge=-5, le=5)
    strength: int = Field(default=0, ge=-5, le=5)
    stamina: int = Field(default=0, ge=-5, le=5)
    presence: int = Field(default=0, ge=-5, le=5)
    communication: int = Field(default=0, ge=-5, le=5)
    dexterity: int = Field(default=0, ge=-5, le=5)
    quickness: int = Field(default=0, ge=-5, le=5)


class CharacteristicsPatch(BaseModel):
    intelligence: int | None = None
    perception: int | None = None
    strength: int | None = None
    stamina: int | None = None
    presence: int | None = None
    communication: int | None = None
    dexterity: int | None = None
    quickness: int | None = None
