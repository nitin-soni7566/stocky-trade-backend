from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.broker_service import api_session_key_for_user, broker_client_for_user


async def account_client_and_token(db: AsyncSession, user: User):
    return await broker_client_for_user(db, user), await api_session_key_for_user(db, user)
