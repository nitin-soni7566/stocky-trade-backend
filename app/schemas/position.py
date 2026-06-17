from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.position import PositionStatus


class PositionResponse(BaseModel):
    id: int
    bot_session_id: int
    symbol: str
    quantity: int
    average_price: Decimal
    ltp: Decimal
    pnl: Decimal
    status: PositionStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TodayPnlResponse(BaseModel):
    pnl: Decimal
