from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os


class Settings(BaseSettings):
    # Основные настройки
    PROJECT_NAME: str = "rule_engine_campings"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"


    # Настройки базы данных (добавим позже)
    DATABASE_URL: Optional[str] = None


    #Settings_db
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")

    )

    def get_db_url(self):
        return (f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")



settings = Settings()


print(settings.get_db_url())
