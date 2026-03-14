from Database.models import BaseModel
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, BigInteger

class SummaryPost(BaseModel):
    __tablename__ = "summary_posts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    summary_id: Mapped[int] = mapped_column(ForeignKey("summaries.id", ondelete="CASCADE"))
    post_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("posts.id", ondelete="CASCADE"))
