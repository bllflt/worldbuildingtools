import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

import httpx
import jwt
from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select

from apifast.config import config
from apifast.db import get_db
from apifast.mdb import get_redis
from apifast.models.model import Character, Image

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

    # Generate JWT token
    payload = {
        "sub": "apifast",
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    token = jwt.encode(payload, config.jwt_secret, algorithm="HS256")

    url = f"{config.llm_proxy_url}/api/v1/captions"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={
                    "character_id": str(character_id),
                    "image_file": str(image_file),
                    "current_description": current_description,
                },
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0,
            )
            print(response.json())
    except httpx.RequestError as exc:
        print(f"An error occurred while requesting {exc.request.url!r}.")
        print(client.requst)
        raise


@router.put("/ai/work/caption/complete", status_code=status.HTTP_202_ACCEPTED)
async def process_caption_result(
    data: CaptionJobResult,
    redis=Depends(get_redis),
    session: Session = Depends(get_db),
):
    character = session.get(Character, data.character_id)
    if character:
        await redis.publish(
            f"{data.character_id}",
            json.dumps(
                {
                    "topic": "reconcile",
                    "character_id": data.character_id,
                    "explanation": data.explanation,
                    "new_description": data.merge,
                }
            ),
        )
