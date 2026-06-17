from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.account import MarginRequest
from app.services.account_service import account_client_and_token
from app.utilities.response import api_response

router = APIRouter()


@router.get("/orders")
async def orders(db: Annotated[AsyncSession, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    client, token = await account_client_and_token(db, current_user)
    return api_response("Account orders fetched", await client.get_orders(token))


@router.get("/orders/{order_id}")
async def order(
    order_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    client, token = await account_client_and_token(db, current_user)
    return api_response("Account order fetched", await client.get_single_order(token, order_id))


@router.get("/trades")
async def trades(db: Annotated[AsyncSession, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    client, token = await account_client_and_token(db, current_user)
    return api_response("Account trades fetched", await client.get_trades(token))


@router.get("/positions")
async def positions(db: Annotated[AsyncSession, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    client, token = await account_client_and_token(db, current_user)
    return api_response("Account positions fetched", await client.get_positions(token))


@router.get("/holdings")
async def holdings(db: Annotated[AsyncSession, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    client, token = await account_client_and_token(db, current_user)
    return api_response("Account holdings fetched", await client.get_holdings(token))


@router.get("/limits")
async def limits(db: Annotated[AsyncSession, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    client, token = await account_client_and_token(db, current_user)
    return api_response("Account limits fetched", await client.get_limits(token))


@router.post("/margin")
async def margin(
    payload: MarginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    client, token = await account_client_and_token(db, current_user)
    return api_response("Account margin fetched", await client.get_margin(token, payload.payload))
