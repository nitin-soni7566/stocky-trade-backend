from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Instrument(Base, TimestampMixin):
    __tablename__ = "instruments"
    __table_args__ = (UniqueConstraint("exchange", "token", name="uq_instruments_exchange_token"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    exchange: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    token: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    symbol: Mapped[str | None] = mapped_column(String(100), index=True, nullable=True)
    tradingsymbol: Mapped[str | None] = mapped_column(String(150), index=True, nullable=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    instrument_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    lot_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
