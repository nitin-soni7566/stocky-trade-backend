from app.broker.definedge_client import DefinedgeClient
from app.schemas.market import PriceResponse, StockResponse


async def get_nifty50_stocks(client: DefinedgeClient) -> list[StockResponse]:
    stocks = await client.get_nifty50_stocks()
    return [StockResponse(symbol=item["symbol"], name=item["name"]) for item in stocks]


async def get_price(client: DefinedgeClient, symbol: str) -> PriceResponse:
    ltp, raw = await client.get_ltp(symbol)
    return PriceResponse(symbol=symbol.upper(), ltp=ltp, raw=raw)
