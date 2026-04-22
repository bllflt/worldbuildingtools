import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlmodel import Session

from apifast.config import config
from apifast.db import get_db
from apifast.models.model import Character, Image

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

    return {"filename": safe_name}
