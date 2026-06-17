from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database.session import get_db
from app.models.order import Order, OrderSide
from app.models.position import Position
from app.models.user import User
from app.schemas.order import OrderResponse, PaperOrderRequest
from app.schemas.position import PositionResponse
from app.services.broker_service import broker_client_for_user
from app.services.paper_trade_service import create_paper_order_from_quote
from app.utilities.response import api_response

router = APIRouter()
positions_router = APIRouter()


async def _create_order(payload: PaperOrderRequest, db: AsyncSession, user: User, side: OrderSide):
    if payload.side != side:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"side must be {side.value}")
    client = await broker_client_for_user(db, user)
    quote = await client.get_quotes(payload.exchange, payload.token)
    ltp = quote.get("ltp") or quote.get("last_price") or quote.get("price")
    if ltp is None:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Definedge LTP was not returned")
    order = await create_paper_order_from_quote(db, user, payload.tradingsymbol, side, payload.quantity, Decimal(str(ltp)))
    await db.commit()
    await db.refresh(order)
    return api_response("Paper order created", OrderResponse.model_validate(order))


@router.post("/buy")
async def buy(
    payload: PaperOrderRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await _create_order(payload, db, current_user, OrderSide.BUY)


@router.post("/sell")
async def sell(
    payload: PaperOrderRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await _create_order(payload, db, current_user, OrderSide.SELL)


@router.get("")
async def list_paper_orders(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    result = await db.execute(
        select(Order)
        .where(Order.user_id == current_user.id, Order.is_paper_order.is_(True))
        .order_by(desc(Order.created_at))
    )
    return api_response("Paper orders fetched", [OrderResponse.model_validate(item) for item in result.scalars().all()])


@router.get("/positions")
async def list_paper_positions(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    result = await db.execute(select(Position).where(Position.user_id == current_user.id).order_by(Position.id.desc()))
    return api_response(
        "Paper positions fetched",
        [PositionResponse.model_validate(item) for item in result.scalars().all()],
    )


@positions_router.get("")
async def list_paper_positions_root(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await list_paper_positions(db, current_user)
