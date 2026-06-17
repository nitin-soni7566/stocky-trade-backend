from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException, status

from app.core.config import get_settings


def _fernet() -> Fernet:
    key = get_settings().encryption_key
    if not key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ENCRYPTION_KEY is not configured",
        )
    return Fernet(key.encode())


def encrypt_value(value: str | None) -> str | None:
    if value is None:
        return None
    return _fernet().encrypt(value.encode()).decode()


def decrypt_value(value: str | None) -> str | None:
    if value is None:
        return None
    try:
        return _fernet().decrypt(value.encode()).decode()
    except InvalidToken as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to decrypt stored broker credential",
        ) from exc
