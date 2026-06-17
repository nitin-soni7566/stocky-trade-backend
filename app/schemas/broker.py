from datetime import datetime

from pydantic import BaseModel, Field


class BrokerCredentialRequest(BaseModel):
    api_key: str = Field(min_length=1)
    api_secret: str = Field(min_length=1)


class BrokerCredentialStatus(BaseModel):
    broker_name: str
    is_active: bool
    has_api_key: bool
    has_api_secret: bool
    has_access_token: bool
    token_expires_at: datetime | None = None


class BrokerTokenResponse(BaseModel):
    has_access_token: bool
    has_susertoken: bool = False
    uid: str | None = None
    actid: str | None = None
    token_expires_at: datetime | None = None


class BrokerOtpGenerateResponse(BaseModel):
    otp_token: str


class BrokerOtpVerifyRequest(BaseModel):
    otp_token: str = Field(min_length=1)
    otp: str = Field(min_length=1)


class BrokerProfileResponse(BaseModel):
    profile: dict


class BrokerSessionStatus(BaseModel):
    is_logged_in: bool
    has_api_session_key: bool
    has_susertoken: bool
    uid: str | None = None
    actid: str | None = None
    token_expires_at: datetime | None = None
