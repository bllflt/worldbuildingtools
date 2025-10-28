from apifast.db import get_db
from apifast.model import Character, CharacterRead
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import selectinload
from sqlmodel import Session, delete, select

router = APIRouter(
    tags=["characters"],
)

@router.get("/characters", response_model=list[CharacterRead])
async def get_characters(
    session:Session = Depends(get_db)
) -> list[Character]:
    statement = select(Character).options(selectinload(Character.roleplaying_attributes))
    return session.exec(statement).all()

@router.get("/characters/{character_id}", response_model=CharacterRead)
async def get_character_by_id(
    character_id: int,
    session:Session = Depends(get_db)
) -> Character:
    statement = (select(Character).where(Character.id == character_id).options(
        selectinload(Character.roleplaying_attributes),
        selectinload(Character.image_attributes)
    ))
    character = session.exec(statement).first()
    if not character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Character with id {character_id} not found")
    return character

@router.delete("/characters/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character_by_id(
    character_id: int,
    session:Session = Depends(get_db)
) -> None:
    character = session.get(Character, character_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with id {character_id} not found"
        )
    session.delete(character)
    session.commit()