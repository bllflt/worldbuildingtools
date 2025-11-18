import json
from dataclasses import dataclass
from pathlib import Path

from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select

from apifast.config import config
from apifast.db import get_db
from apifast.model import Character, Image
from apifast.mdb import get_redis

QUEUE_NAME = "work_queue"

router = APIRouter()


@dataclass(slots=True)
class CaptionJobRequest:
    image: str


@dataclass(slots=True)
class CaptionJobResult:
    character_id: int
    explanation: str | None
    merge: str | None


@router.put("/ai/work/caption/request", status_code=status.HTTP_202_ACCEPTED)
async def enque_caption_work(
    data: CaptionJobRequest,
    redis=Depends(get_redis),
    session: Session = Depends(get_db),
):
    character_id = (
        session.exec(
            select(Image).where(Image.uri == data.image, Image.character_id is not None)
        )
        .one()
        .character_id
    )
    current_description = session.get(Character, character_id).appearance
    image_file = Path(config.image_dir).joinpath(data.image)
    await redis.lpush(
        QUEUE_NAME,
        json.dumps(
            {
                "image_file": str(image_file),
                "current_description": current_description,
                "character_id": character_id,
            }
        ),
    )


@router.put("/ai/work/caption/complete", status_code=status.HTTP_202_ACCEPTED)
async def process_caption_result(
    data: CaptionJobResult,
    session: Session = Depends(get_db),
):
    character = session.get(Character, data.character_id)
    if character:
        if character.appearance == "":
            character.appearance = data.merge
            session.commit()
