from pydantic import BaseModel, Field

from charservice.modules.arsmagica.enums import CategoryCode, VirtueFlawLevelCode


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
