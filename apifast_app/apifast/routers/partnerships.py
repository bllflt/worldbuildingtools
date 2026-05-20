from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from apifast.db import get_db
from apifast.models.model import Partnership, PartnershipWrite
from apifast.services.partnerships import PartnershipQuery, PartnershipService

router = APIRouter(
    tags=["partnerships"],
)


@router.get("/partnerships", response_model=list[Partnership])
async def get_partnerships(
    session: Session = Depends(get_db),
    faction: bool = Query(False, description="Filter by factions"),
) -> list[Partnership]:
    return PartnershipService.get_partnerships(
        session, PartnershipQuery(faction_only=faction)
    )


@router.post("/partnerships", status_code=201, response_model=Partnership)
async def create_partnership(
    partnership: PartnershipWrite, session: Session = Depends(get_db)
) -> Partnership:
    return PartnershipService.create_partnership(session, partnership)


@router.get(
    "/partnerships/{partnership_id}",
    response_model=Partnership,
    response_model_exclude={"id"},
)
async def get_partnership_by_id(
    partnership_id: int, session: Session = Depends(get_db)
) -> Partnership:
    partnership = PartnershipService.get_partnership_by_id(session, partnership_id)
    if not partnership:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return partnership


@router.put("/partnerships/{partnership_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_partnership_by_id(
    partnership: PartnershipWrite,
    partnership_id: int,
    session: Session = Depends(get_db),
) -> None:
    try:
        PartnershipService.update_partnership(session, partnership_id, partnership)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.delete("/partnerships/{partnership_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_partnership_by_id(
    partnership_id: int, session: Session = Depends(get_db)
) -> None:
    try:
        PartnershipService.delete_partnership(session, partnership_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
