from datetime import date, datetime, time, timezone
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database.session import get_db
from app.models.position import Position
from app.models.trade import Trade
from app.models.user import User
from app.schemas.position import PositionResponse, TodayPnlResponse
from app.utilities.response import api_response

router = APIRouter()


@router.get("/positions")
async def list_positions(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    result = await db.execute(select(Position).where(Position.user_id == current_user.id).order_by(Position.id.desc()))
    positions = [PositionResponse.model_validate(position) for position in result.scalars().all()]
    return api_response("Positions fetched", positions)


@router.get("/pnl/today")
async def today_pnl(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    start = datetime.combine(date.today(), time.min, tzinfo=timezone.utc)
    end = datetime.combine(date.today(), time.max, tzinfo=timezone.utc)
    result = await db.execute(
        select(func.coalesce(func.sum(Trade.pnl), 0)).where(
            Trade.user_id == current_user.id,
            Trade.created_at >= start,
            Trade.created_at <= end,
        )
    )
    pnl = result.scalar_one() or Decimal("0")
    return api_response("Today's P&L fetched", TodayPnlResponse(pnl=pnl))
