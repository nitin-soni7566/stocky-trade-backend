from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bot_session import BotSession
from app.models.order import Order, OrderSide, OrderStatus, OrderType
from app.models.position import Position, PositionStatus
from app.models.trade import Trade
from app.models.user import User


async def open_paper_position(
    db: AsyncSession,
    user: User,
    session: BotSession,
    symbol: str,
    quantity: int,
    ltp: Decimal,
    side: OrderSide = OrderSide.BUY,
) -> Position:
    signed_quantity = quantity if side == OrderSide.BUY else -quantity
    order = Order(
        user_id=user.id,
        bot_session_id=session.id,
        symbol=symbol.upper(),
        side=side,
        order_type=OrderType.MARKET,
        quantity=quantity,
        price=ltp,
        status=OrderStatus.PAPER_PLACED,
        is_paper_order=True,
    )
    db.add(order)
    await db.flush()

    db.add(Trade(user_id=user.id, order_id=order.id, symbol=symbol.upper(), side=side, quantity=quantity, price=ltp))
    position = Position(
        user_id=user.id,
        bot_session_id=session.id,
        symbol=symbol.upper(),
        quantity=signed_quantity,
        average_price=ltp,
        ltp=ltp,
        pnl=Decimal("0"),
        status=PositionStatus.OPEN,
    )
    db.add(position)
    await db.flush()
    return position


async def create_paper_order_from_quote(
    db: AsyncSession,
    user: User,
    symbol: str,
    side: OrderSide,
    quantity: int,
    ltp: Decimal,
    session: BotSession | None = None,
) -> Order:
    order = Order(
        user_id=user.id,
        bot_session_id=session.id if session else None,
        symbol=symbol.upper(),
        side=side,
        order_type=OrderType.MARKET,
        quantity=quantity,
        price=ltp,
        status=OrderStatus.PAPER_PLACED,
        is_paper_order=True,
    )
    db.add(order)
    await db.flush()
    db.add(Trade(user_id=user.id, order_id=order.id, symbol=symbol.upper(), side=side, quantity=quantity, price=ltp))
    return order


async def close_paper_position(db: AsyncSession, user: User, position: Position, ltp: Decimal) -> Decimal:
    pnl = (ltp - position.average_price) * position.quantity
    order = Order(
        user_id=user.id,
        bot_session_id=position.bot_session_id,
        symbol=position.symbol,
        side=OrderSide.SELL,
        order_type=OrderType.MARKET,
        quantity=position.quantity,
        price=ltp,
        status=OrderStatus.PAPER_EXITED,
        is_paper_order=True,
    )
    db.add(order)
    await db.flush()
    db.add(
        Trade(
            user_id=user.id,
            order_id=order.id,
            symbol=position.symbol,
            side=OrderSide.SELL,
            quantity=position.quantity,
            price=ltp,
            pnl=pnl,
        )
    )
    position.ltp = ltp
    position.pnl = pnl
    position.status = PositionStatus.CLOSED
    await db.flush()
    return pnl
