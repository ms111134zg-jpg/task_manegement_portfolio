from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    POSTGRE_HOST: str
    POSTGRE_PORT: int
    POSTGRE_DB: str
    POSTGRE_USER: str
    POSTGRE_PW: str
    APP_ENV: str = "dev"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRE_USER}:{self.POSTGRE_PW}"
            f"@{self.POSTGRE_HOST}:{self.POSTGRE_PORT}/{self.POSTGRE_DB}"
        )


settings = Settings()