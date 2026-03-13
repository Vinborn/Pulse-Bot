from datetime import datetime

from Database.models import BaseModel
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, BigInteger, String

class Summary(BaseModel):
    __tablename__ = "summaries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    channel_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("channels.id", ondelete="CASCADE"), nullable=False)

    topic: Mapped[str] = mapped_column(String(255))
    content: Mapped[str]
    last_included_post_id: Mapped[int] = mapped_column(BigInteger)

    summary_date: Mapped[datetime] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False)

    # content_hash: Mapped[str] - Если текст постов изменился или отредактирован — хэш изменится