from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import JSONResponse
from sqlmodel import Session

from apifast.db import get_db
from apifast.model import Character, CharacterRead, CharacterWrite
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
    return CharacterService.create_character(session, character)


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
    try:
        CharacterService.update_character(session, character_id, character)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.delete("/characters/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character_by_id(
    character_id: int, session: Session = Depends(get_db)
) -> None:
    try:
        CharacterService.delete_character(session, character_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with id {character_id} not found",
        ) from exc
