from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, UserResponse
from app.services.auth_service import login_user, register_user
from app.utilities.response import api_response

router = APIRouter()


@router.post("/register")
async def register(
    payload: RegisterRequest, db: Annotated[AsyncSession, Depends(get_db)]
):
    user = await register_user(db, payload)
    return api_response(
        "User registered successfully", UserResponse.model_validate(user)
    )


@router.post("/login")
async def login(payload: LoginRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    token = await login_user(db, payload)
    return api_response("Login successful", token)


@router.get("/me")
async def me(current_user: Annotated[User, Depends(get_current_user)]):
    return api_response(
        "Current user fetched", UserResponse.model_validate(current_user)
    )
