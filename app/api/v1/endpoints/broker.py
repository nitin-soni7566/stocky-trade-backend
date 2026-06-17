from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.broker import BrokerCredentialRequest, BrokerOtpVerifyRequest
from app.services.broker_service import (
    broker_client_for_user,
    credential_status,
    generate_broker_otp,
    get_credentials,
    save_credentials,
    session_status,
    verify_broker_otp,
)
from app.utilities.response import api_response

router = APIRouter()


@router.post("/credentials")
async def credentials_create(
    payload: BrokerCredentialRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    status = await save_credentials(db, current_user, payload)
    return api_response("Broker credentials saved", status)


@router.get("/credentials/status")
async def credentials_status(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    credentials = await get_credentials(db, current_user)
    return api_response("Broker credential status fetched", credential_status(credentials))


@router.post("/token/generate")
async def token_generate(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    otp = await generate_broker_otp(db, current_user)
    return api_response("Broker OTP generated", otp)


@router.post("/login/request-otp")
async def login_request_otp(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    otp = await generate_broker_otp(db, current_user)
    return api_response("Broker OTP generated", otp)


@router.post("/token/verify")
async def token_verify(
    payload: BrokerOtpVerifyRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    token_status = await verify_broker_otp(db, current_user, payload)
    return api_response("Broker token verified and saved", token_status)


@router.post("/login/verify-otp")
async def login_verify_otp(
    payload: BrokerOtpVerifyRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    token_status = await verify_broker_otp(db, current_user, payload)
    return api_response("Broker session verified and saved", token_status)


@router.get("/session/status")
async def broker_session_status(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return api_response("Broker session status fetched", await session_status(db, current_user))


@router.get("/profile")
async def profile(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    client = await broker_client_for_user(db, current_user)
    return api_response("Broker profile fetched", {"profile": await client.get_profile()})
