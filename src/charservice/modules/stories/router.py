from collections.abc import Sequence

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from charservice.db import get_db
from charservice.modules.stories.service import SagaService

router = APIRouter()


@router.get("/get_permitted_stories")
async def get_permitted_stories(
    user_id: int = Query(None, description="User ID to check permissions for"),
    session: Session = Depends(get_db),
) -> Sequence[int]:

    return SagaService.get_permitted_stories(session, user_id)
