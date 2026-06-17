from decimal import Decimal

from pydantic import BaseModel, Field


class StockResponse(BaseModel):
    symbol: str
    name: str
    exchange: str = "NSE"


class PriceResponse(BaseModel):
    symbol: str
    ltp: Decimal
    raw: dict | None = None


class MasterDownloadRequest(BaseModel):
    master: str = Field(default="nsecash", pattern="^(nsecash|nsefno|allmaster)$")


class InstrumentResponse(BaseModel):
    id: int
    exchange: str
    token: str
    symbol: str | None = None
    tradingsymbol: str | None = None
    name: str | None = None
    instrument_type: str | None = None
    lot_size: int | None = None

    model_config = {"from_attributes": True}


class HistoryQuery(BaseModel):
    segment: str
    token: str
    timeframe: str
    from_date: str
    to_date: str
