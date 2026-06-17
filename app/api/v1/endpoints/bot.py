from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.bot import BotSessionResponse, BotStartRequest, BotStatusResponse
from app.services.bot_service import current_bot, start_bot, stop_bot
from app.api.v1.endpoints.positions import today_pnl
from app.utilities.response import api_response

router = APIRouter()


@router.post("/start")
async def start(
    payload: BotStartRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    session = await start_bot(db, current_user, payload)
    return api_response("Paper bot started", BotSessionResponse.model_validate(session))


@router.post("/stop")
async def stop(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    session = await stop_bot(db, current_user)
    return api_response("Paper bot stopped", BotSessionResponse.model_validate(session))


@router.get("/status")
async def status(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    session = await current_bot(db, current_user)
    data = BotStatusResponse(
        running=session is not None,
        session=BotSessionResponse.model_validate(session) if session else None,
    )
    return api_response("Bot status fetched", data)


@router.get("/pnl/today")
async def bot_today_pnl(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await today_pnl(db, current_user)
