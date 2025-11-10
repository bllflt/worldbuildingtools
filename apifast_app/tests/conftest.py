from typing import Generator

import pytest
from apifast.db import enable_foreign_keys, get_db
from apifast.main import app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
enable_foreign_keys(engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Creates a clean, independent session for each test."""
    # 1. Create tables in the test database
    SQLModel.metadata.create_all(bind=engine)

    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()  # Rolls back all changes made during the test
    connection.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """TestClient that uses the test session."""

    def override_get_db():
        """Override the dependency to use the test session."""
        try:
            yield db_session  # Yield the session from the db_session fixture
        finally:
            # Note: No session.close() here as it's handled by db_session cleanup
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    # Cleanup: Remove the override after the tests
    del app.dependency_overrides[get_db]
