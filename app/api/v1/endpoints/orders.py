from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database.session import get_db
from app.models.order import Order
from app.models.user import User
from app.schemas.order import OrderResponse
from app.utilities.response import api_response

router = APIRouter()


@router.get("")
async def list_orders(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    result = await db.execute(select(Order).where(Order.user_id == current_user.id).order_by(desc(Order.created_at)))
    orders = [OrderResponse.model_validate(order) for order in result.scalars().all()]
    return api_response("Orders fetched", orders)


@router.get("/{order_id}")
async def get_order(
    order_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    result = await db.execute(select(Order).where(Order.id == order_id, Order.user_id == current_user.id))
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return api_response("Order fetched", OrderResponse.model_validate(order))
