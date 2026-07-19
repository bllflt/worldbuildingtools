from contextlib import contextmanager
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

from charservice.config import config

engine = create_engine(config.database_uri)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


get_db_context = contextmanager(get_db)
