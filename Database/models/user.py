from Database.models import BaseModel
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger

class User(BaseModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str | None]
    language: Mapped[str]