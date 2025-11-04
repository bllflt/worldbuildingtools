from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

from apifast.config import config

router = APIRouter()


@router.get("/images/{image_uri}", response_class=FileResponse, include_in_schema=False)
async def get_images(
    image_uri: str,
):
    return Path(config.image_dir).joinpath(image_uri)
