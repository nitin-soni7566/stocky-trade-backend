from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.bot_session import BotSession, BotStatus, TradeMode
from app.models.user import User


async def validate_bot_start(db: AsyncSession, user: User, trade_mode: TradeMode, quantity: int) -> None:
    if quantity <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity must be greater than zero")
    if trade_mode == TradeMode.LIVE and not get_settings().enable_live_trading:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Live trading is disabled")

    result = await db.execute(
        select(BotSession).where(BotSession.user_id == user.id, BotSession.status == BotStatus.RUNNING)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already has a running bot")
