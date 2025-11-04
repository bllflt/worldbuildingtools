from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlmodel import select

from apifast.db import Session, get_db
from apifast.model import (
    PartnershipParticipant,
    PartnershipParticipantRead,
    PartnershipParticipantWrite,
)

router = APIRouter()


@router.get(
    "/partnerships/{pid}/participants", response_model=list[PartnershipParticipantWrite]
)
async def get_participants(
    pid: int,
    session: Session = Depends(get_db),
) -> list[PartnershipParticipantWrite]:
    found = session.execute(
        text("select exists(select 1 from partnerships where id = :pid)"), {"pid": pid}
    ).scalar_one()
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    results = session.exec(
        select(PartnershipParticipant).where(
            PartnershipParticipant.partnership_id == pid
        )
    ).all()
    return [PartnershipParticipantWrite.model_validate(r) for r in results]


@router.post("/partnerships/{pid}/participants", status_code=status.HTTP_204_NO_CONTENT)
async def add_participants(
    pid: int,
    participants: list[PartnershipParticipantWrite],
    session: Session = Depends(get_db),
):
    found = session.execute(
        text("select exists(select 1 from partnerships where id = :pid)"),
        {"pid": pid},
    ).scalar_one()
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    rv = []
    for p in participants:
        found = session.execute(
            text("select exists(select 1 from character where id = :cid)"),
            {"cid": p.character_id},
        ).scalar_one()
        if not found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Character with id {p.character_id} not found",
            )
        rv.append(
            PartnershipParticipant.model_validate(
                p.model_dump() | {"partnership_id": pid},
            )
        )
    session.add_all(rv)
    session.commit()
    return rv


@router.get(
    "/partnerships/{pid}/participants/{cid}", response_model=PartnershipParticipantRead
)
async def get_participant(
    pid: int, cid: int, session: Session = Depends(get_db)
) -> PartnershipParticipantRead:
    pp = session.exec(
        select(PartnershipParticipant).where(
            PartnershipParticipant.partnership_id == pid,
            PartnershipParticipant.character_id == cid,
        )
    ).one_or_none()
    if not pp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return pp


@router.delete(
    "/partnerships/{pid}/participants/{cid}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_participant(
    pid: int, cid: int, session: Session = Depends(get_db)
) -> None:
    pp = session.exec(
        select(PartnershipParticipant).where(
            PartnershipParticipant.partnership_id == pid,
            PartnershipParticipant.character_id == cid,
        )
    ).one_or_none()
    if not pp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    session.delete(pp)
    session.commit()


@router.put(
    "/partnershiops/{pid}/participants/{cid}", status_code=status.HTTP_204_NO_CONTENT
)
async def update_participant(
    pid: int,
    cid: int,
    participant: PartnershipParticipant,
    session: Session = Depends(get_db),
) -> None:
    pp = session.exec(
        select(PartnershipParticipant).where(
            PartnershipParticipant.partnership_id == pid,
            PartnershipParticipant.character_id == cid,
        )
    ).one_or_none()
    if not pp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    pp.sqlmodel_update(participant)
    session.commit()
