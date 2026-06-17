import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utc_now


class OrderSide(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, enum.Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class OrderStatus(str, enum.Enum):
    PAPER_PLACED = "PAPER_PLACED"
    PAPER_EXITED = "PAPER_EXITED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    bot_session_id: Mapped[int | None] = mapped_column(ForeignKey("bot_sessions.id", ondelete="SET NULL"), nullable=True)
    symbol: Mapped[str] = mapped_column(String(50), nullable=False)
    side: Mapped[OrderSide] = mapped_column(Enum(OrderSide, name="order_side"), nullable=False)
    order_type: Mapped[OrderType] = mapped_column(Enum(OrderType, name="order_type"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus, name="order_status"), nullable=False)
    broker_order_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_paper_order: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    bot_session = relationship("BotSession", back_populates="orders")
    trades = relationship("Trade", back_populates="order")
