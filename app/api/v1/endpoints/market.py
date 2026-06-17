from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.broker.master_file_service import download_master_file, search_instruments
from app.schemas.market import InstrumentResponse, MasterDownloadRequest
from app.services.broker_service import broker_client_for_user
from app.services.market_service import get_nifty50_stocks, get_price
from app.utilities.response import api_response

router = APIRouter()


@router.get("/nifty50")
async def nifty50(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    client = await broker_client_for_user(db, current_user)
    return api_response("NIFTY 50 stocks fetched", await get_nifty50_stocks(client))


@router.post("/master/download")
async def master_download(
    payload: MasterDownloadRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    _ = current_user
    return api_response("Master file downloaded", await download_master_file(db, payload.master))


@router.get("/search")
async def search(
    query: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    _ = current_user
    instruments = await search_instruments(db, query)
    return api_response("Instruments fetched", [InstrumentResponse.model_validate(item) for item in instruments])


@router.get("/quote/{exchange}/{token}")
async def quote(
    exchange: str,
    token: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    client = await broker_client_for_user(db, current_user)
    return api_response("Quote fetched", await client.get_quotes(exchange, token))


@router.get("/security-info/{exchange}/{token}")
async def security_info(
    exchange: str,
    token: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    client = await broker_client_for_user(db, current_user)
    return api_response("Security info fetched", await client.get_security_info(exchange, token))


@router.get("/history")
async def history(
    segment: str,
    token: str,
    timeframe: str,
    from_date: str,
    to_date: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    client = await broker_client_for_user(db, current_user)
    data = await client.get_history(segment, token, timeframe, from_date, to_date)
    return api_response("Historical data fetched", data)


@router.get("/price/{symbol}")
async def price(
    symbol: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    client = await broker_client_for_user(db, current_user)
    return api_response("Current price fetched", await get_price(client, symbol))
