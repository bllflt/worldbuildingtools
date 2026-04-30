import json
import logging
import shutil
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

import httpx
import jwt
from apifast.config import config
from apifast.db import get_db
from apifast.mdb import get_redis
from apifast.models.model import Character, Image
from fastapi import (APIRouter, Depends, File, Form, HTTPException, UploadFile,
                     status)
from fastapi.responses import FileResponse
from sqlmodel import Session

router = APIRouter()


@router.get("/images/{image_uri}", response_class=FileResponse, include_in_schema=False)
async def get_images(
    image_uri: str,
):
    return Path(config.image_dir).joinpath(image_uri)


@router.post("/characters/upload-image")
async def upload_character_image(
    character_id: int = Form(
        ..., description="The ID of the character to associate the image with"
    ),
    image: UploadFile = File(..., description="The image file to upload"),
    session: Session = Depends(get_db),
    redis=Depends(get_redis),
):
    # Verify character existence
    character = session.get(Character, character_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with id {character_id} not found",
        )

    file_extension = Path(image.filename).suffix if image.filename else ""
    safe_name = f"{uuid.uuid4().hex}{file_extension}"

    image_dir = Path(config.image_dir)
    image_dir.mkdir(parents=True, exist_ok=True)

    save_path = image_dir / safe_name
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    db_image = Image(character_id=character_id, uri=safe_name)
    session.add(db_image)
    session.commit()

    await redis.publish(
        f"{character_id}",
        json.dumps(
            {
                "topic": "image",
                "filename": safe_name,
            }
        )
    )


    return {"filename": safe_name}


@dataclass(slots=True)
class ImageJobRequest:
    character_id: str


@router.post("/characters/generate-image")
async def generate_character_image(message: ImageJobRequest) -> None:

    # Generate JWT token
    payload = {
        "sub": "apifast",
        "exp": datetime.now() + timedelta(hours=1),
    }
    token = jwt.encode(payload, config.jwt_secret, algorithm="HS256")

    try:
        url = f"{config.llm_proxy_url}/api/v1/images"
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={
                    "character_id": str(message.character_id),
                },
                headers={"Authorization": f"Bearer {token}"},
            )
            logging.debug(f"LLM proxy response: {response}")
            response.raise_for_status()
    except Exception:
        return None
