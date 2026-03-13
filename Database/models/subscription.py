from Database.models import BaseModel
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, BigInteger

class UserSubscription(BaseModel):
    __tablename__ = "user_subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    channel_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("channels.id", ondelete="CASCADE"))