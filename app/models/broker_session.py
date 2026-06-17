from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class BrokerSession(Base, TimestampMixin):
    __tablename__ = "broker_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    broker_name: Mapped[str] = mapped_column(String(50), default="definedge", nullable=False)
    api_session_key: Mapped[str] = mapped_column(Text, nullable=False)
    susertoken: Mapped[str | None] = mapped_column(Text, nullable=True)
    uid: Mapped[str | None] = mapped_column(String(100), nullable=True)
    actid: Mapped[str | None] = mapped_column(String(100), nullable=True)
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
