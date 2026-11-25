from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    weather_mode: str = "live"
    request_timeout_seconds: float = 12.0
    humidity_elevated_threshold: float = Field(default=75.0, ge=0, le=100)
    humidity_high_threshold: float = Field(default=85.0, ge=0, le=100)
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
