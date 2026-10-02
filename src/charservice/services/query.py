from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, TypeVar
from uuid import UUID

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlmodel import SQLModel, select
from sqlmodel.sql.expression import Select, SelectOfScalar

T = TypeVar("T", bound=SQLModel)


@dataclass(slots=True)
class BaseQuery:
    """Generic query parameters for retrieving SQLModel objects."""

    sort: str | None = None
    name: str | None = None
    fields: Sequence[str] | set[str] | None = None


def build_query_statement(
    model: type[T],
    *,
    fields: Sequence[str] | set[str] | None = None,
    sort: str | None = None,
    name: str | None = None,
    where_clauses: Sequence[Any] | None = None,
    options: Sequence[Any] | None = None,
) -> Select | SelectOfScalar:
    """Build a SQLModel select query with generic field selection, sorting, and filtering."""
    if fields:
        stmt = select(*(getattr(model, f) for f in fields))
    else:
        stmt = select(model)

    if where_clauses:
        for clause in where_clauses:
            stmt = stmt.where(clause)

    if sort and hasattr(model, sort):
        stmt = stmt.order_by(getattr(model, sort))

    if name and hasattr(model, "name"):
        stmt = stmt.where(getattr(model, "name").icontains(name))

    if not fields and options:
        stmt = stmt.options(*options)

    return stmt


def validate_fields(
    fields: str | None, model_schema: type[BaseModel]
) -> list[str] | None:
    """Validate requested query fields against a Pydantic model schema."""
    if not fields:
        return None
    include_fields = fields.split(",")
    valid_fields = [f for f in include_fields if f in model_schema.model_fields]
    if len(valid_fields) != len(include_fields):
        invalid_fields = set(include_fields) - set(valid_fields)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid fields requested: {', '.join(invalid_fields)}",
        )
    return include_fields


def format_fields_response(
    results: Sequence[Any], fields: Sequence[str]
) -> list[dict[str, Any]]:
    """Format row results when specific fields were requested into a list of dicts."""
    rv = []
    for row in results:
        filtered_item = {}
        is_row_sequence = isinstance(row, (tuple, Sequence)) and not isinstance(
            row, (str, bytes)
        )
        for i, k in enumerate(fields):
            val = row[i] if is_row_sequence else row
            if isinstance(val, UUID):
                val = str(val)
            filtered_item[k] = val
        rv.append(filtered_item)
    return rv
