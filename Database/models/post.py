from datetime import datetime

from Database.models import BaseModel
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, BigInteger

class Post(BaseModel):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    channel_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("channels.id", ondelete="CASCADE"), nullable=False)
    tg_id: Mapped[int] = mapped_column(BigInteger)

    content: Mapped[str | None]
    created_at: Mapped[datetime]

    # media: Mapped[str]