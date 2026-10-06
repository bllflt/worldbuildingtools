from collections.abc import Callable, Sequence
from typing import Any, TypeVar
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlmodel import Session

from charservice.db import get_db
from charservice.modules.arsmagica.schemas import (
    CharacterFlawSchema,
    CharacterVirtueSchema,
    FlawSchema,
    VirtueSchema,
)
from charservice.modules.arsmagica.service import FlawService, VirtueService
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
    fields: str | None,
    schema: type[SchemaT],
    get_traits: Callable[[Session, BaseQuery | None], Sequence[Any]],
) -> list[SchemaT] | Response:
    include_fields = validate_fields(fields, schema) if fields else None
    results = get_traits(
        session,
        BaseQuery(sort=sort, name=name, fields=include_fields),
    )
    if include_fields is None:
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
    fields: str | None = Query(None, description="Fields to return"),
    session: Session = Depends(get_db),
) -> list[VirtueSchema] | Response:
    return _read_traits(
        session,
        sort=sort,
        name=name,
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
    fields: str | None = Query(None, description="Fields to return"),
    session: Session = Depends(get_db),
) -> list[FlawSchema] | Response:
    return _read_traits(
        session,
        sort=sort,
        name=name,
        fields=fields,
        schema=FlawSchema,
        get_traits=FlawService.get_traits,
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
