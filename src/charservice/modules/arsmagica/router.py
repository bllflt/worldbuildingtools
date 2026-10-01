from fastapi import APIRouter, Depends
from sqlmodel import Session

from charservice.db import get_db
from charservice.modules.arsmagica.schemas import VirtueSchema
from charservice.modules.arsmagica.service import VirtueService

router = APIRouter(tags=["Ars Magica"])


@router.get("/virtues")
async def read_virtue(session: Session = Depends(get_db)) -> list[VirtueSchema]:
    results = VirtueService.get_virtues(session)
    return [VirtueSchema.model_validate(v) for v in results]


@router.get("/virtues/{virtue_name}")
async def read_virtue_details(
    virtue_name: str, session: Session = Depends(get_db)
) -> VirtueSchema:
    result = VirtueService.get_virtue_by_name(session, virtue_name)
    return VirtueSchema.model_validate(result)
