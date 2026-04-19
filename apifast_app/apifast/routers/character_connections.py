from fastapi import APIRouter, Depends, Query, status

from apifast.db import Session, get_db
from apifast.models.model import SocialConnection
from apifast.services.character_connections import CharacterConnectionsService

router = APIRouter(
    tags=["characters"],
)


@router.get(
    "/characters/{character_id}/connections",
    response_model=list[SocialConnection],
    responses={
        status.HTTP_200_OK: {
            "description": "A list of social connections for the character.",
            "model": list[SocialConnection],
        },
    },
)
async def get_connections_by_charcter_id(
    character_id: int,
    degree: int = Query(
        description="Degree of social graph to return (0-3)",
        ge=0,
        le=3,
        default=0,
    ),
    session: Session = Depends(get_db),
) -> list[SocialConnection]:
    return CharacterConnectionsService.get_connections_by_character_id(
        session, character_id, degree
    )
