import bcrypt
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, min_length=1)
    hashed_password: str

    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), self.hashed_password)

    def save_password(self, password: str) -> None:
        salt = bcrypt.gensalt(rounds=12)
        self.hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
