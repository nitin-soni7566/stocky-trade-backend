from datetime import datetime

from pydantic import BaseModel, Field

from app.models.bot_session import BotStatus, TradeMode, TradeType
from app.models.order import OrderSide


class BotStartRequest(BaseModel):
    trade_mode: TradeMode = TradeMode.PAPER
    trade_type: TradeType = TradeType.INTRADAY
    exchange: str = Field(default="NSE", min_length=1, max_length=20)
    token: str | None = Field(default=None, min_length=1, max_length=50)
    tradingsymbol: str | None = Field(default=None, min_length=1, max_length=100)
    symbol: str | None = Field(default=None, min_length=1, max_length=50)
    timeframe: str = Field(default="5m", min_length=1, max_length=50)
    side: OrderSide = OrderSide.BUY
    quantity: int = Field(gt=0)
    paper_trade: bool = True


class BotSessionResponse(BaseModel):
    id: int
    trade_mode: TradeMode
    trade_type: TradeType
    exchange: str | None = None
    token: str | None = None
    symbol: str
    timeframe: str
    quantity: int
    status: BotStatus
    started_at: datetime | None
    stopped_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class BotStatusResponse(BaseModel):
    running: bool
    session: BotSessionResponse | None = None
