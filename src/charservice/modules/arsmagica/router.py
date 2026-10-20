from collections.abc import Callable, Sequence
from typing import Any, Literal, TypeVar
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlmodel import Session

from charservice.db import get_db
from charservice.modules.arsmagica.schemas import (
    AbilitySchema,
    CharacterAbilitySchema,
    CharacterFlawSchema,
    CharacterVirtueSchema,
    FlawSchema,
    VirtueSchema,
)
from charservice.modules.arsmagica.service import (
    AbilityService,
    FlawService,
    VirtueService,
)
from charservice.services.query import (
    BaseQuery,
    format_fields_response,
    validate_fields,
)

router = APIRouter(tags=["Ars Magica"])

SchemaT = TypeVar("SchemaT", bound=BaseModel)


def _read_traits(
    session: Session,
    *,
    sort: str | None,
    name: str | None,
    q: str | None,
    mode: Literal["keyword", "semantic", "hybrid"] | None,
    limit: int | None,
    fields: str | None,
    schema: type[SchemaT],
    get_traits: Callable[[Session, BaseQuery | None], Sequence[Any]],
) -> list[SchemaT] | Response:
    if (q is not None or mode is not None) and (q is None or not q.strip()):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A non-empty q value is required for search.",
        )
    include_fields = validate_fields(fields, schema) if fields else None
    results = get_traits(
        session,
        BaseQuery(
            sort=sort,
            name=name,
            fields=include_fields,
            q=q,
            mode=mode,
            limit=limit,
        ),
    )
    if include_fields is None:
        if mode in ("semantic", "hybrid"):
            results = [row[0] for row in results]
        return [schema.model_validate(trait) for trait in results]
    return JSONResponse(content=format_fields_response(results, include_fields))


@router.get(
    "/virtues",
    response_model=None,
    responses={
        200: {
            "description": (
                "A list of virtues. Returns a list of `VirtueSchema` objects by default,"
                + " or a list of dictionaries with specific fields if the `fields` query "
                + "parameter is used."
            ),
            "model": list[VirtueSchema],
        },
    },
)
async def read_virtue(
    sort: str | None = Query(None, description="Field to sort by"),
    name: str | None = Query(None, description="Filter by name"),
    q: str | None = Query(None, description="Search query"),
    mode: Literal["keyword", "semantic", "hybrid"] | None = Query(
        None, description="Search mode"
    ),
    limit: int | None = Query(None, ge=0, description="Maximum results to return"),
    fields: str | None = Query(None, description="Fields to return"),
    session: Session = Depends(get_db),
) -> list[VirtueSchema] | Response:
    return _read_traits(
        session,
        sort=sort,
        name=name,
        q=q,
        mode=mode,
        limit=limit,
        fields=fields,
        schema=VirtueSchema,
        get_traits=VirtueService.get_traits,
    )


@router.get(
    "/flaws",
    response_model=None,
    responses={
        200: {
            "description": (
                "A list of flaws. Returns a list of `FlawSchema` objects by default,"
                + " or a list of dictionaries with specific fields if the `fields` query "
                + "parameter is used."
            ),
            "model": list[FlawSchema],
        },
    },
)
async def read_flaws(
    sort: str | None = Query(None, description="Field to sort by"),
    name: str | None = Query(None, description="Filter by name"),
    q: str | None = Query(None, description="Search query"),
    mode: Literal["keyword", "semantic", "hybrid"] | None = Query(
        None, description="Search mode"
    ),
    limit: int | None = Query(None, ge=0, description="Maximum results to return"),
    fields: str | None = Query(None, description="Fields to return"),
    session: Session = Depends(get_db),
) -> list[FlawSchema] | Response:
    return _read_traits(
        session,
        sort=sort,
        name=name,
        q=q,
        mode=mode,
        limit=limit,
        fields=fields,
        schema=FlawSchema,
        get_traits=FlawService.get_traits,
    )


@router.get(
    "/abilities",
    response_model=None,
    responses={
        200: {
            "description": (
                "A list of abilities. Returns a list of `AbilitySchema` objects by "
                "default, or a list of dictionaries with specific fields if the "
                "`fields` query parameter is used."
            ),
            "model": list[AbilitySchema],
        },
    },
)
async def read_abilities(
    sort: str | None = Query(None, description="Field to sort by"),
    name: str | None = Query(None, description="Filter by name"),
    q: str | None = Query(None, description="Search query"),
    mode: Literal["keyword", "semantic", "hybrid"] | None = Query(
        None, description="Search mode"
    ),
    limit: int | None = Query(None, ge=0, description="Maximum results to return"),
    fields: str | None = Query(None, description="Fields to return"),
    session: Session = Depends(get_db),
) -> list[AbilitySchema] | Response:
    return _read_traits(
        session,
        sort=sort,
        name=name,
        q=q,
        mode=mode,
        limit=limit,
        fields=fields,
        schema=AbilitySchema,
        get_traits=AbilityService.get_traits,
    )


@router.get("/virtues/{virtue_name}")
async def read_virtue_details(
    virtue_name: str, session: Session = Depends(get_db)
) -> VirtueSchema:
    result = VirtueService.get_virtue_by_name(session, virtue_name)
    return VirtueSchema.model_validate(result)


@router.get("/flaws/{flaw_name}")
async def read_flaw_details(
    flaw_name: str, session: Session = Depends(get_db)
) -> FlawSchema:
    result = FlawService.get_flaw_by_name(session, flaw_name)
    return FlawSchema.model_validate(result)


@router.get("/abilities/{ability_name}")
async def read_ability_details(
    ability_name: str, session: Session = Depends(get_db)
) -> AbilitySchema:
    result = AbilityService.get_ability_by_name(session, ability_name)
    return AbilitySchema.model_validate(result)


@router.get("/characters/{character_id}/virtues")
async def read_virtues_of_character(
    character_id: UUID, session: Session = Depends(get_db)
) -> list[str]:
    results = VirtueService.get_virtues_of_character(session, character_id)
    return list(results)


@router.get("/characters/{character_id}/flaws")
async def read_flaws_of_character(
    character_id: UUID, session: Session = Depends(get_db)
) -> list[str]:
    results = FlawService.get_flaws_of_character(session, character_id)
    return list(results)


@router.get("/characters/{character_id}/abilities")
async def read_abilities_of_character(
    character_id: UUID, session: Session = Depends(get_db)
) -> list[str]:
    results = AbilityService.get_abilities_of_character(session, character_id)
    return list(results)


@router.post(
    "/characters/{character_id}/virtues/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def update_virtue_of_character(
    character_id: UUID,
    virtue: CharacterVirtueSchema,
    session: Session = Depends(get_db),
) -> None:
    VirtueService.update_virtue_of_character(session, character_id, virtue.name)


@router.post(
    "/characters/{character_id}/flaws/", status_code=status.HTTP_204_NO_CONTENT
)
async def update_flaw_of_character(
    character_id: UUID,
    flaw: CharacterFlawSchema,
    session: Session = Depends(get_db),
) -> None:
    FlawService.update_flaw_of_character(session, character_id, flaw.name)


@router.post(
    "/characters/{character_id}/abilities/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def update_ability_of_character(
    character_id: UUID,
    ability: CharacterAbilitySchema,
    session: Session = Depends(get_db),
) -> None:
    AbilityService.update_ability_of_character(session, character_id, ability.name)


@router.delete(
    "/characters/{character_id}/virtues/{virtue}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_virtue_of_character(
    character_id: UUID,
    virtue: str,
    session: Session = Depends(get_db),
) -> None:
    VirtueService.remove_virtue_of_character(session, character_id, virtue)

@router.delete(
    "/characters/{character_id}/flaws/{flaw}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_flaw_of_character(
    character_id: UUID,
    flaw: str,
    session: Session = Depends(get_db),
) -> None:
    FlawService.remove_flaw_of_character(session, character_id, flaw)


@router.delete(
    "/characters/{character_id}/abilities/{ability}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_ability_of_character(
    character_id: UUID,
    ability: str,
    session: Session = Depends(get_db),
) -> None:
    AbilityService.remove_ability_of_character(session, character_id, ability)
