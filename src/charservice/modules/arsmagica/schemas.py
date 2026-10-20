from pydantic import BaseModel, Field

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

    name: str = Field(..., description="Name of the virtue")


class CharacterFlawSchema(BaseModel):
    model_config = {
        "from_attributes": True,
    }

    name: str = Field(..., description="Name of the flaw")


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


class CharacterAbilitySchema(BaseModel):
    model_config = {
        "from_attributes": True,
    }

    name: str = Field(..., description="Name of the ability")
