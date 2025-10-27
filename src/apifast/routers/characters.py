from fastapi import APIRouter, Depends
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from apifast.db import get_db
from apifast.model import Character, CharacterRead

router = APIRouter()

@router.get("/characters", response_model=list[CharacterRead])
async def get_characters(
    session:Session = Depends(get_db)
) -> list[Character]:
    statement = select(Character).options(selectinload(Character.roleplaying_attributes))
    return session.exec(statement).all()
