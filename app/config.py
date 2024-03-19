from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_PASS: str
    DB_USER: str
    DB_NAME: str

    SECRET_KEY: str
    ALGORITHM: str
    
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    SU_EMAIL: List[str]

    class Config:
        env_file = ".env-non-dev"


settings = Settings()

DATABASE_URL = (f"postgresql+asyncpg://{settings.DB_USER}:"
                f"{settings.DB_PASS}@{settings.DB_HOST}:"
                f"{settings.DB_PORT}/{settings.DB_NAME}")
