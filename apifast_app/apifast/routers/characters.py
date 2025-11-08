from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from apifast.db import get_db
from apifast.model import Character, CharacterRead, CharacterWrite, Image, Roleplaying
from apifast.services.characters import CharacterQuery, CharacterService

router = APIRouter(
    tags=["characters"],
)


@router.get(
    "/characters",
    response_model=None,
    responses={
        200: {
            "description": (
                "A list of characters. Returns a list of `CharacterRead` objects by default,"
                + " or a list of dictionaries with specific fields if the `fields` query "
                + "parameter is used."
            ),
            "model": list[CharacterRead],
        },
    },
)
async def get_characters_list(
    sort: str | None = Query(None, description="Field to sort by"),
    name: str | None = Query(None, description="filter by name"),
    fields: str | None = Query(None, description="Fields to return"),
    session: Session = Depends(get_db),
) -> list[CharacterRead] | Response:
    include_fields: set[str] | None = None

    if fields:
        include_fields = fields.split(",")

        valid_fields = [
            field
            for field in include_fields
            if field in CharacterRead.model_fields.keys()
        ]
        if len(valid_fields) != len(include_fields):
            invalid_fields = set(include_fields) - set(valid_fields)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid fields requested: {', '.join(invalid_fields)}",
            )

    results = CharacterService.get_characters(
        session,
        CharacterQuery(
            sort=sort,
            name=name,
            fields=include_fields,
        ),
    )
    if fields is None:
        return [CharacterRead.model_validate(c) for c in results]
    rv = []
    for row in results:
        filtered_item = {k: row[i] for i, k in enumerate(include_fields)}
        rv.append(filtered_item)
    return JSONResponse(content=rv)


@router.post(
    "/characters", status_code=status.HTTP_201_CREATED, response_model=CharacterRead
)
async def create_character(
    character: CharacterWrite, session: Session = Depends(get_db)
) -> Character:
    character_data = character.model_dump(exclude={"attributes", "images"})
    db_character = Character.model_validate(character_data)

    db_character.roleplaying_attributes = [
        Roleplaying(characteristic=attr) for attr in character.roleplaying
    ]
    db_character.image_attributes = [Image(uri=img) for img in character.images]

    session.add(db_character)
    session.commit()
    session.refresh(db_character)
    return db_character


@router.get("/characters/{character_id}", response_model=CharacterRead)
async def get_character_by_id(
    character_id: int, session: Session = Depends(get_db)
) -> Character:
    
    character = CharacterService.get_character_by_id(session, character_id) 
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with id {character_id} not found",
        )
    return character


@router.put("/characters/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_character_by_id(
    character: CharacterWrite,
    character_id: int,
    session: Session = Depends(get_db),
) -> None:
    statement = (
        select(Character)
        .where(Character.id == character_id)
        .options(
            selectinload(Character.roleplaying_attributes),
            selectinload(Character.image_attributes),
        )
    )
    db_character = session.exec(statement).one_or_none()
    if not db_character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    update_data = character.model_dump(exclude={"roleplaying", "images"})
    for key, value in update_data.items():
        setattr(db_character, key, value)

    db_character.roleplaying_attributes.clear()
    db_character.roleplaying_attributes.extend(
        [Roleplaying(characteristic=attr) for attr in character.roleplaying]
    )
    db_character.image_attributes.clear()
    db_character.image_attributes.extend([Image(uri=img) for img in character.images])

    session.commit()


@router.delete("/characters/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character_by_id(
    character_id: int, session: Session = Depends(get_db)
) -> None:
    character = session.get(Character, character_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with id {character_id} not found",
        )
    session.delete(character)
    session.commit()
