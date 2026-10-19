from collections.abc import Sequence
from dataclasses import dataclass
from functools import lru_cache
from importlib import import_module
from typing import Any, Literal, TypeAlias, TypeVar
from uuid import UUID

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import case, or_
from sqlmodel import SQLModel, select
from sqlmodel.sql.expression import Select, SelectOfScalar

T = TypeVar("T", bound=SQLModel)
SearchMode: TypeAlias = Literal["keyword", "semantic", "hybrid"]
EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"
QUERY_INSTRUCTION_PREFIX = "Represent this sentence for searching relevant passages: "


@lru_cache(maxsize=1)
def _get_embedding_model() -> Any:
    SentenceTransformer = import_module("sentence_transformers").SentenceTransformer
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def _encode_query(query: str) -> Any:
    return _get_embedding_model().encode(f"{QUERY_INSTRUCTION_PREFIX}{query}")


def _model_field(model: type[T], field: str) -> Any:
    return getattr(model, field)


@dataclass(slots=True)
class BaseQuery:
    """Generic query parameters for retrieving SQLModel objects."""

    sort: str | None = None
    name: str | None = None
    fields: Sequence[str] | set[str] | None = None
    q: str | None = None
    mode: SearchMode | None = None
    limit: int | None = None


def build_query_statement(
    model: type[T],
    *,
    fields: Sequence[str] | set[str] | None = None,
    sort: str | None = None,
    name: str | None = None,
    q: str | None = None,
    mode: SearchMode | None = None,
    limit: int | None = None,
    where_clauses: Sequence[Any] | None = None,
    options: Sequence[Any] | None = None,
) -> Select[Any] | SelectOfScalar[Any]:
    """Build a SQLModel select query with generic field selection, sorting, and filtering."""
    search_mode = mode or ("keyword" if q is not None else None)
    if search_mode not in (None, "keyword", "semantic", "hybrid"):
        raise ValueError(f"Unsupported search mode: {search_mode}")
    if search_mode is not None and (q is None or not q.strip()):
        raise ValueError("A non-empty q value is required when mode is specified.")
    if limit is not None and limit < 0:
        raise ValueError("limit must be greater than or equal to 0.")

    if fields:
        stmt = select(*(getattr(model, f) for f in fields))
    else:
        stmt = select(model)

    distance_expr = None
    keyword_match = None
    if search_mode in ("keyword", "hybrid"):
        keyword_columns = [
            getattr(model, field)
            for field in ("name", "description")
            if hasattr(model, field)
        ]
        if not keyword_columns:
            raise ValueError(
                f"{model.__name__} has no name or description field to search."
            )
        if q is None:
            raise ValueError("A non-empty q value is required when mode is specified.")
        keyword_match = or_(*(column.icontains(q) for column in keyword_columns))
        if search_mode == "keyword":
            stmt = stmt.where(keyword_match)

    if search_mode in ("semantic", "hybrid"):
        if not hasattr(model, "embedding"):
            raise ValueError(f"{model.__name__} does not have an embedding field.")
        if q is None:
            raise ValueError("A non-empty q value is required when mode is specified.")
        distance_expr = _model_field(model, "embedding").cosine_distance(
            _encode_query(q)
        )
        stmt = stmt.add_columns(distance_expr)

    if where_clauses:
        for clause in where_clauses:
            stmt = stmt.where(clause)

    sort_field = _model_field(model, sort) if sort and hasattr(model, sort) else None
    if search_mode == "hybrid":
        if keyword_match is None or distance_expr is None:
            raise RuntimeError("Hybrid search expressions were not initialized.")
        keyword_rank = case((keyword_match, 0), else_=1)
        order_by = [keyword_rank, distance_expr]
        if sort_field is not None:
            order_by.append(sort_field)
        stmt = stmt.order_by(*order_by)
    elif distance_expr is not None:
        order_by = [distance_expr]
        if sort_field is not None:
            order_by.append(sort_field)
        stmt = stmt.order_by(*order_by)
    elif sort_field is not None:
        stmt = stmt.order_by(sort_field)

    if name and hasattr(model, "name"):
        stmt = stmt.where(_model_field(model, "name").icontains(name))

    if not fields and options:
        stmt = stmt.options(*options)

    if limit is not None:
        stmt = stmt.limit(limit)

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
