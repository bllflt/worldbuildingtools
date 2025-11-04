from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from apifast.db import get_db
from apifast.model import Partnership, PartnershipWrite

router = APIRouter()


@router.get("/partnerships", response_model=list[Partnership])
async def get_partnerships(
    session: Session = Depends(get_db),
) -> list[Partnership]:
    results = session.exec(select(Partnership)).all()
    return results


@router.post("/partnerships", status_code=201, response_model=Partnership)
async def create_partnership(
    partnership: PartnershipWrite, session: Session = Depends(get_db)
) -> Partnership:
    db_partnership = Partnership.model_validate(partnership.model_dump())
    session.add(db_partnership)
    session.commit()
    session.refresh(db_partnership)
    return db_partnership


@router.get("/partnerships/{partnership_id}", response_model=Partnership)
async def get_partnership_by_id(
    partnership_id: int, session: Session = Depends(get_db)
) -> Partnership:
    partnership = session.get(Partnership, partnership_id)
    if not partnership:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return partnership


@router.delete("/partnerships/{partnership_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_partnership_by_id(
    partnership_id: int, session: Session = Depends(get_db)
) -> None:
    partnership = session.get(Partnership, partnership_id)
    if not partnership:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    session.delete(partnership)
    session.commit()


@router.put("/partnerships/{partnership_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_partnership_by_id(
    partnership: PartnershipWrite,
    partnership_id: int,
    session: Session = Depends(get_db),
):
    db_partnership = session.get(Partnership, partnership_id)
    if not db_partnership:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    db_partnership.sqlmodel_update(partnership)
    session.commit()
    session.refresh(db_partnership)
