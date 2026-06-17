from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.broker.definedge_client import DefinedgeClient
from app.models.broker_credential import BrokerCredential
from app.models.broker_session import BrokerSession
from app.models.user import User
from app.schemas.broker import (
    BrokerCredentialRequest,
    BrokerCredentialStatus,
    BrokerOtpGenerateResponse,
    BrokerOtpVerifyRequest,
    BrokerSessionStatus,
    BrokerTokenResponse,
)
from app.utilities.encryption import decrypt_value, encrypt_value


async def save_credentials(db: AsyncSession, user: User, payload: BrokerCredentialRequest) -> BrokerCredentialStatus:
    result = await db.execute(
        select(BrokerCredential).where(
            BrokerCredential.user_id == user.id,
            BrokerCredential.broker_name == "definedge",
        )
    )
    credentials = result.scalar_one_or_none()
    if credentials is None:
        credentials = BrokerCredential(user_id=user.id, broker_name="definedge", api_key="")
        db.add(credentials)

    credentials.api_key = encrypt_value(payload.api_key)
    credentials.api_secret = encrypt_value(payload.api_secret)
    credentials.access_token = None
    credentials.token_expires_at = None
    credentials.is_active = True
    await db.commit()
    await db.refresh(credentials)
    return credential_status(credentials)


async def get_credentials(db: AsyncSession, user: User) -> BrokerCredential | None:
    result = await db.execute(
        select(BrokerCredential).where(
            BrokerCredential.user_id == user.id,
            BrokerCredential.broker_name == "definedge",
            BrokerCredential.is_active.is_(True),
        )
    )
    return result.scalar_one_or_none()


def credential_status(credentials: BrokerCredential | None) -> BrokerCredentialStatus:
    return BrokerCredentialStatus(
        broker_name=credentials.broker_name if credentials else "definedge",
        is_active=bool(credentials and credentials.is_active),
        has_api_key=bool(credentials and credentials.api_key),
        has_api_secret=bool(credentials and credentials.api_secret),
        has_access_token=bool(credentials and credentials.access_token),
        token_expires_at=credentials.token_expires_at if credentials else None,
    )


async def generate_broker_otp(db: AsyncSession, user: User) -> BrokerOtpGenerateResponse:
    credentials = await get_credentials(db, user)
    if credentials is None:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Broker credentials not found")

    client = DefinedgeClient(
        api_key=decrypt_value(credentials.api_key),
        api_secret=decrypt_value(credentials.api_secret),
    )
    data = await client.generate_otp()
    otp_token = data.get("otp_token") or data.get("otpToken") or data.get("token")
    if not otp_token:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Definedge OTP token was not returned")
    return BrokerOtpGenerateResponse(otp_token=otp_token)


async def verify_broker_otp(db: AsyncSession, user: User, payload: BrokerOtpVerifyRequest) -> BrokerTokenResponse:
    credentials = await get_credentials(db, user)
    if credentials is None:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Broker credentials not found")

    client = DefinedgeClient()
    token, expires_at, data = await client.verify_otp(payload.otp_token, payload.otp)
    susertoken = data.get("susertoken")
    uid = data.get("uid")
    actid = data.get("actid")

    credentials.access_token = encrypt_value(token)
    credentials.token_expires_at = expires_at
    session = BrokerSession(
        user_id=user.id,
        broker_name="definedge",
        api_session_key=encrypt_value(token),
        susertoken=encrypt_value(susertoken),
        uid=uid,
        actid=actid,
        token_expires_at=expires_at,
    )
    db.add(session)
    await db.commit()
    return BrokerTokenResponse(
        has_access_token=True,
        has_susertoken=bool(susertoken),
        uid=uid,
        actid=actid,
        token_expires_at=expires_at,
    )


async def get_latest_broker_session(db: AsyncSession, user: User) -> BrokerSession | None:
    result = await db.execute(
        select(BrokerSession)
        .where(BrokerSession.user_id == user.id, BrokerSession.broker_name == "definedge")
        .order_by(desc(BrokerSession.created_at))
    )
    return result.scalar_one_or_none()


async def session_status(db: AsyncSession, user: User) -> BrokerSessionStatus:
    session = await get_latest_broker_session(db, user)
    return BrokerSessionStatus(
        is_logged_in=bool(session),
        has_api_session_key=bool(session and session.api_session_key),
        has_susertoken=bool(session and session.susertoken),
        uid=session.uid if session else None,
        actid=session.actid if session else None,
        token_expires_at=session.token_expires_at if session else None,
    )


async def broker_client_for_user(db: AsyncSession, user: User) -> DefinedgeClient:
    from fastapi import HTTPException, status

    credentials = await get_credentials(db, user)
    session = await get_latest_broker_session(db, user)
    token = session.api_session_key if session else credentials.access_token if credentials else None
    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Generate broker access token first")
    return DefinedgeClient(access_token=decrypt_value(token))


async def api_session_key_for_user(db: AsyncSession, user: User) -> str:
    from fastapi import HTTPException, status

    session = await get_latest_broker_session(db, user)
    if session is None or not session.api_session_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Complete Definedge OTP login first")
    return decrypt_value(session.api_session_key)
