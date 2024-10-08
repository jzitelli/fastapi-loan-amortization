import secrets

from pydantic_settings import BaseSettings #, SettingsConfigDict


class Settings(BaseSettings):
    # model_config = SettingsConfigDict(
    #     env_file=".env", env_ignore_empty=True, extra="ignore"
    # )
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    EMAIL_TEST_USER: str = "test@example.com"
    FIRST_SUPERUSER: str = "admin"
    FIRST_SUPERUSER_PASSWORD: str = "ok"


settings = Settings()  # type: ignore
