from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from fastapi.responses import JSONResponse
from sqlmodel import Session

from charservice.db import get_db
from charservice.modules.arsmagica.schemas import CharacterVirtueSchema, VirtueSchema
from charservice.modules.arsmagica.service import VirtueQuery, VirtueService
from charservice.services.query import format_fields_response, validate_fields

router = APIRouter(tags=["Ars Magica"])


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
    include_fields: list[str] | None = None

    if fields:
        include_fields = validate_fields(fields, VirtueSchema)

    results = VirtueService.get_virtues(
        session,
        VirtueQuery(
            sort=sort,
            name=name,
            fields=include_fields,
        ),
    )
    if fields is None:
        return [VirtueSchema.model_validate(v) for v in results]
    return JSONResponse(content=format_fields_response(results, include_fields))


@router.get("/virtues/{virtue_name}")
async def read_virtue_details(
    virtue_name: str, session: Session = Depends(get_db)
) -> VirtueSchema:
    result = VirtueService.get_virtue_by_name(session, virtue_name)
    return VirtueSchema.model_validate(result)


@router.get("/characters/{character_id}/virtues")
async def read_virtues_of_character(
    character_id: UUID, session: Session = Depends(get_db)
) -> list[str]:
    results = VirtueService.get_virtues_of_character(session, character_id)
    return results


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
