from sqlalchemy import BigInteger

from Database.models import BaseModel
from sqlalchemy.orm import Mapped, mapped_column

class Channel(BaseModel):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    tg_link: Mapped[str] = mapped_column(unique=True)
    title: Mapped[str]

    last_message_id: Mapped[int | None] = mapped_column(BigInteger)