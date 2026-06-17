from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "intraday-trading-backend"
    api_v1_prefix: str = "/api/v1"
    environment: str = "local"

    database_url: str = Field(default="postgresql+asyncpg://postgres:postgres@localhost:5432/intraday_trading")
    jwt_secret_key: str = Field(default="change-me")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    encryption_key: str = Field(default="")

    definedge_base_url: str = ""
    definedge_login_url: str = ""
    definedge_trading_base_url: str = "https://integrate.definedgesecurities.com/dart/v1"
    definedge_auth_base_url: str = "https://signin.definedgesecurities.com/auth/realms/debroking/dsbpkc"
    definedge_data_base_url: str = "https://data.definedgesecurities.com/sds"
    definedge_ws_url: str = "wss://trade.definedgesecurities.com/NorenWSTRTP/"
    enable_live_trading: bool = False
    redis_url: str | None = None

    @property
    def trading_base_url(self) -> str:
        return self.definedge_trading_base_url or self.definedge_base_url

    @property
    def auth_base_url(self) -> str:
        return self.definedge_auth_base_url or self.definedge_login_url

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("database_url")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
