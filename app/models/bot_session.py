import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utc_now


class TradeMode(str, enum.Enum):
    PAPER = "PAPER"
    LIVE = "LIVE"


class TradeType(str, enum.Enum):
    INTRADAY = "INTRADAY"
    DAILY = "DAILY"


class BotStatus(str, enum.Enum):
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    FAILED = "FAILED"


class BotSession(Base):
    __tablename__ = "bot_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    trade_mode: Mapped[TradeMode] = mapped_column(Enum(TradeMode, name="trade_mode"), nullable=False)
    trade_type: Mapped[TradeType] = mapped_column(Enum(TradeType, name="trade_type"), nullable=False)
    exchange: Mapped[str | None] = mapped_column(String(20), nullable=True)
    token: Mapped[str | None] = mapped_column(String(50), nullable=True)
    symbol: Mapped[str] = mapped_column(String(50), nullable=False)
    timeframe: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[BotStatus] = mapped_column(Enum(BotStatus, name="bot_status"), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    stopped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    user = relationship("User", back_populates="bot_sessions")
    orders = relationship("Order", back_populates="bot_session")
    positions = relationship("Position", back_populates="bot_session")
