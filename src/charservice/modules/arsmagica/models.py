from sqlalchemy import CheckConstraint
from sqlmodel import Field, Relationship, SQLModel


class Category(SQLModel, table=True):
    __tablename__ = "categories"  # type: ignore[override]

    code: str = Field(default=None, primary_key=True, min_length=1)


class Virtue(SQLModel, table=True):
    __tablename__ = "virtues"  # type: ignore[override]

    name: str = Field(default=None, primary_key=True, min_length=1)
    description: str = Field(min_length=1)
    category: str = Field(foreign_key="categories.code", ondelete="CASCADE")
    level: str = Field(
        sa_column_args=[CheckConstraint("level IN ('Minor', 'Major', 'Free')")],
    )
    tainted: bool | None = Field(default=False)
    conflicts_with: list["VirtueConflict"] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "Virtue.name == VirtueConflict.virtue",
        }
    )
    requires_one_of: list["VirtueRequirement"] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "Virtue.name == VirtueRequirement.virtue",
        }
    )


class VirtueConflict(SQLModel, table=True):
    __tablename__ = "virtue_conflicts"  # type: ignore[override]

    virtue: str = Field(
        foreign_key="virtues.name", ondelete="CASCADE", primary_key=True
    )
    conflicts_with: str = Field(
        foreign_key="virtues.name", ondelete="CASCADE", primary_key=True
    )


class VirtueRequirement(SQLModel, table=True):
    __tablename__ = "virtue_requirements"  # type: ignore[override]

    virtue: str = Field(
        foreign_key="virtues.name", ondelete="CASCADE", primary_key=True
    )
    requires: str = Field(
        foreign_key="virtues.name", ondelete="CASCADE", primary_key=True
    )
