from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from charservice.db import get_db
from charservice.models.model import (
    PartnershipParticipantRead,
    PartnershipParticipantWrite,
)
from charservice.services.partnership_participants import PartnershipParticipantService

router = APIRouter(
    tags=["partnership participants"],
)


@router.get(
    "/partnerships/{pid}/participants", response_model=list[PartnershipParticipantWrite]
)
async def get_participants(
    pid: int,
    session: Session = Depends(get_db),
) -> list[PartnershipParticipantWrite]:
    try:
        results = PartnershipParticipantService.get_participants(session, pid)
        return [PartnershipParticipantWrite.model_validate(r) for r in results]
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post("/partnerships/{pid}/participants", status_code=status.HTTP_204_NO_CONTENT)
async def add_participants(
    pid: int,
    participants: list[PartnershipParticipantWrite],
    session: Session = Depends(get_db),
) -> None:
    try:
        PartnershipParticipantService.add_participants(session, pid, participants)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.get(
    "/partnerships/{pid}/participants/{cid}", response_model=PartnershipParticipantRead
)
async def get_participant(
    pid: int, cid: int, session: Session = Depends(get_db)
) -> PartnershipParticipantRead:
    try:
        pp = PartnershipParticipantService.get_participant(session, pid, cid)
        if not pp:
            raise ValueError(f"Participant not found in partnership {pid}")
        return pp
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.put(
    "/partnerships/{pid}/participants/{cid}", status_code=status.HTTP_204_NO_CONTENT
)
async def update_participant(
    pid: int,
    cid: int,
    participant: PartnershipParticipantWrite,
    session: Session = Depends(get_db),
) -> None:
    try:
        PartnershipParticipantService.update_participant(session, pid, cid, participant)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.delete(
    "/partnerships/{pid}/participants/{cid}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_participant(
    pid: int, cid: int, session: Session = Depends(get_db)
) -> None:
    try:
        PartnershipParticipantService.delete_participant(session, pid, cid)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
