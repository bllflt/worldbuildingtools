from sqlalchemy import CheckConstraint
from sqlmodel import Field, SQLModel


class Saga(SQLModel, table=True):
    __tablename__ = "sagas" # type: ignore[override]

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(min_length=1)


class SagaXUser(SQLModel, table=True):
    __tablename__ = "saga_x_user" # type: ignore[override]

    saga_id: int = Field(primary_key=True, foreign_key="sagas.id", ondelete="CASCADE")
    user_id: int = Field(primary_key=True)
    role: str = Field(
        sa_column_args=[CheckConstraint("role IN ('owner', 'writer', 'reader')")],
    )
