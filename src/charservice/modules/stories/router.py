from collections.abc import Sequence
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from charservice.db import get_db
from charservice.modules.auth.service import get_permitted_stories as gms
from charservice.modules.stories.service import SagaService

router = APIRouter()


@router.get("/get_permitted_stories")
async def get_permitted_stories(
    user_id: int = Query(None, description="User ID to check permissions for"),
    session: Session = Depends(get_db),
) -> Sequence[int]:

    return SagaService.get_permitted_stories(session, user_id)


@router.get("/get_permitted_stories_by_ids")
async def get_permitted_stories_by_ids(
    session: Session = Depends(get_db), permitted_stories: Sequence[int] = Depends(gms)
) -> list[dict[str, str | Any | None]]:

    return SagaService.get_permitted_story_names_by_ids(session, permitted_stories)
