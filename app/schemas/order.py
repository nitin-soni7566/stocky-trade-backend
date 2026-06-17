from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel
from pydantic import Field

from app.models.order import OrderSide, OrderStatus, OrderType


class OrderResponse(BaseModel):
    id: int
    bot_session_id: int | None
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: int
    price: Decimal
    status: OrderStatus
    broker_order_id: str | None
    is_paper_order: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PaperOrderRequest(BaseModel):
    exchange: str = Field(default="NSE", min_length=1, max_length=20)
    token: str = Field(min_length=1, max_length=50)
    tradingsymbol: str = Field(min_length=1, max_length=100)
    side: OrderSide
    quantity: int = Field(gt=0)
