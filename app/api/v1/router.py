from fastapi import APIRouter

from app.api.v1.endpoints import account, auth, bot, broker, live_orders, market, orders, paper_orders, positions

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(broker.router, prefix="/broker", tags=["broker"])
api_router.include_router(market.router, prefix="/market", tags=["market"])
api_router.include_router(account.router, prefix="/account", tags=["account"])
api_router.include_router(bot.router, prefix="/bot", tags=["bot"])
api_router.include_router(paper_orders.router, prefix="/paper-orders", tags=["paper-orders"])
api_router.include_router(paper_orders.positions_router, prefix="/paper-positions", tags=["paper-positions"])
api_router.include_router(live_orders.router, prefix="/live-orders", tags=["live-orders"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(positions.router, tags=["positions"])
