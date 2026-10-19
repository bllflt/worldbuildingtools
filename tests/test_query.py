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
    assert "ORDER BY flaws.embedding <=> " in sql
    assert sql.index("ORDER BY flaws.embedding <=> ") < sql.index(", flaws.name")
    assert "LIMIT" in sql


def test_query_encoder_uses_bge_search_instruction(monkeypatch):
    encoded_text = None

    class EmbeddingModel:
        def encode(self, text):
            nonlocal encoded_text
            encoded_text = text
            return [0.0] * 384

    monkeypatch.setattr(query_service, "_get_embedding_model", lambda: EmbeddingModel())

    query_service._encode_query("able to gain knowledge from reading")

    assert (
        encoded_text
        == "Represent this sentence for searching relevant passages: "
        "able to gain knowledge from reading"
    )


def test_hybrid_query_orders_keyword_matches_before_semantic_distance(monkeypatch):
    monkeypatch.setattr(query_service, "_encode_query", lambda _: [0.0] * 384)

    statement = build_query_statement(Flaw, q="curse", mode="hybrid")

    sql = str(statement.compile(dialect=postgresql.dialect()))
    assert "ORDER BY CASE WHEN" in sql
    assert "flaws.embedding <=> " in sql
    assert "flaws.description ILIKE" in sql


def test_hybrid_query_keeps_similarity_ranking_ahead_of_sort(monkeypatch):
    monkeypatch.setattr(query_service, "_encode_query", lambda _: [0.0] * 384)

    statement = build_query_statement(Flaw, q="curse", mode="hybrid", sort="name")

    sql = str(statement.compile(dialect=postgresql.dialect()))
    order_clause = sql.split("ORDER BY ", 1)[1]
    assert order_clause.index("CASE WHEN") < order_clause.index("flaws.embedding <=> ")
    assert order_clause.index("flaws.embedding <=> ") < order_clause.index(
        ", flaws.name"
    )
