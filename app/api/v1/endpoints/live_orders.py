from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.services.account_service import account_client_and_token
from app.utilities.response import api_response

router = APIRouter()


@router.post("/place")
async def place(
    payload: dict,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    client, token = await account_client_and_token(db, current_user)
    return api_response("Live order placed", await client.place_order(payload, token))


@router.post("/modify")
async def modify(
    payload: dict,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    client, token = await account_client_and_token(db, current_user)
    return api_response("Live order modified", await client.modify_order(payload, token))


@router.post("/cancel/{order_id}")
async def cancel(
    order_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    client, token = await account_client_and_token(db, current_user)
    return api_response("Live order cancelled", await client.cancel_order(order_id, token))
