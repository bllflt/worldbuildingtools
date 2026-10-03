from pydantic import BaseModel, Field

from charservice.modules.arsmagica.enums import CategoryCode, VirtueFlawLevelCode


class VirtueSchema(BaseModel):
    model_config = {
        "from_attributes": True,
    }

    name: str = Field(..., description="Name of the virtue", min_length=1)
    description: str = Field(..., description="Description of the virtue", min_length=1)
    category: CategoryCode = Field(..., description="Category of the virtue")
    level: VirtueFlawLevelCode = Field(..., description="Level of the virtue")
    tainted: bool = Field(False, description="Whether the virtue is tainted")


class CharacterVirtueSchema(BaseModel):
    model_config = {
        "from_attributes": True,
    }

    name: str = Field(..., description="Name of the virtue")
