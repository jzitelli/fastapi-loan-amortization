from pydantic_settings import BaseSettings #, SettingsConfigDict


class Settings(BaseSettings):
    # model_config = SettingsConfigDict(
    #     env_file=".env", env_ignore_empty=True, extra="ignore"
    # )
    FIRST_SUPERUSER: str = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "changethis"


settings = Settings()  # type: ignore
