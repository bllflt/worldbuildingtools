from contextlib import contextmanager
from typing import Generator

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

from apifast.config import config

SQLALCHEMY_DATABASE_URL = config.database_uri


def enable_foreign_keys(engine: Engine):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, _connection_record):
        # the sqlite3 driver will not set PRAGMA foreign_keys
        # if autocommit=False; set to True temporarily
        ac = dbapi_connection.autocommit
        dbapi_connection.autocommit = True

        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

        # restore previous autocommit setting
        dbapi_connection.autocommit = ac


engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
enable_foreign_keys(engine)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
