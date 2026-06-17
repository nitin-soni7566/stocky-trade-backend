from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bot_session import BotSession, BotStatus, TradeMode
from app.models.position import Position, PositionStatus
from app.models.user import User
from app.schemas.bot import BotStartRequest
from app.services.broker_service import broker_client_for_user
from app.services.paper_trade_service import close_paper_position, open_paper_position
from app.services.risk_service import validate_bot_start


async def start_bot(db: AsyncSession, user: User, payload: BotStartRequest) -> BotSession:
    await validate_bot_start(db, user, payload.trade_mode, payload.quantity)
    if payload.trade_mode != TradeMode.PAPER or not payload.paper_trade:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Phase 1 supports paper trading only")
    if not payload.token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="token is required")

    client = await broker_client_for_user(db, user)
    quote = await client.get_quotes(payload.exchange, payload.token)
    raw_ltp = quote.get("ltp") or quote.get("last_price") or quote.get("price")
    if raw_ltp is None:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Definedge LTP was not returned")
    ltp = Decimal(str(raw_ltp))
    symbol = (payload.tradingsymbol or payload.symbol or payload.token).upper()
    session = BotSession(
        user_id=user.id,
        trade_mode=payload.trade_mode,
        trade_type=payload.trade_type,
        exchange=payload.exchange.upper(),
        token=payload.token,
        symbol=symbol,
        timeframe=payload.timeframe,
        quantity=payload.quantity,
        status=BotStatus.RUNNING,
        started_at=datetime.now(timezone.utc),
    )
    db.add(session)
    await db.flush()
    await open_paper_position(db, user, session, symbol, payload.quantity, ltp, payload.side)
    await db.commit()
    await db.refresh(session)
    return session


async def stop_bot(db: AsyncSession, user: User) -> BotSession:
    result = await db.execute(
        select(BotSession).where(BotSession.user_id == user.id, BotSession.status == BotStatus.RUNNING)
    )
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No running bot session found")

    client = await broker_client_for_user(db, user)
    if session.exchange and session.token:
        quote = await client.get_quotes(session.exchange, session.token)
        raw_ltp = quote.get("ltp") or quote.get("last_price") or quote.get("price")
        if raw_ltp is None:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Definedge LTP was not returned")
        ltp = Decimal(str(raw_ltp))
    else:
        ltp, _ = await client.get_ltp(session.symbol)
    positions = await db.execute(
        select(Position).where(
            Position.user_id == user.id,
            Position.bot_session_id == session.id,
            Position.status == PositionStatus.OPEN,
        )
    )
    for position in positions.scalars().all():
        await close_paper_position(db, user, position, ltp)

    session.status = BotStatus.STOPPED
    session.stopped_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(session)
    return session


async def current_bot(db: AsyncSession, user: User) -> BotSession | None:
    result = await db.execute(
        select(BotSession)
        .where(BotSession.user_id == user.id, BotSession.status == BotStatus.RUNNING)
        .order_by(desc(BotSession.created_at))
    )
    return result.scalar_one_or_none()
