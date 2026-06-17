import enum
from decimal import Decimal

from sqlalchemy import Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class PositionStatus(str, enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class Position(Base, TimestampMixin):
    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    bot_session_id: Mapped[int] = mapped_column(ForeignKey("bot_sessions.id", ondelete="CASCADE"), nullable=False)
    symbol: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    average_price: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    ltp: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    pnl: Mapped[Decimal] = mapped_column(Numeric(14, 4), default=0, nullable=False)
    status: Mapped[PositionStatus] = mapped_column(Enum(PositionStatus, name="position_status"), nullable=False)

    bot_session = relationship("BotSession", back_populates="positions")
