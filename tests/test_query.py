from sqlalchemy.dialects import postgresql

from charservice.modules.arsmagica.models import Flaw
from charservice.services import query as query_service
from charservice.services.query import build_query_statement


def test_query_statement_without_search_parameters_preserves_basic_select():
    statement = build_query_statement(Flaw)

    assert str(statement) == "SELECT flaws.name, flaws.description, flaws.category, flaws.level, flaws.embedding \nFROM flaws"


def test_keyword_query_filters_fields_and_limit():
    statement = build_query_statement(
        Flaw,
        fields=["name"],
        q="cursed",
        mode="keyword",
        limit=5,
    )

    compiled = statement.compile(dialect=postgresql.dialect())
    assert "flaws.name ILIKE" in str(compiled)
    assert "flaws.description ILIKE" in str(compiled)
    assert "LIMIT" in str(compiled)


def test_semantic_query_selects_distance_and_supports_fields_sort_and_limit(
    monkeypatch,
):
    monkeypatch.setattr(query_service, "_encode_query", lambda _: [0.0] * 384)

    statement = build_query_statement(
        Flaw,
        fields=["name", "description"],
        q="a persistent curse",
        mode="semantic",
        sort="name",
        limit=10,
    )

    compiled = statement.compile(dialect=postgresql.dialect())
    sql = str(compiled)
    assert "flaws.name, flaws.description, flaws.embedding <=> " in sql
    assert "ORDER BY flaws.name" in sql
    assert "LIMIT" in sql


def test_hybrid_query_orders_keyword_matches_before_semantic_distance(monkeypatch):
    monkeypatch.setattr(query_service, "_encode_query", lambda _: [0.0] * 384)

    statement = build_query_statement(Flaw, q="curse", mode="hybrid")

    sql = str(statement.compile(dialect=postgresql.dialect()))
    assert "ORDER BY CASE WHEN" in sql
    assert "flaws.embedding <=> " in sql
    assert "flaws.description ILIKE" in sql
