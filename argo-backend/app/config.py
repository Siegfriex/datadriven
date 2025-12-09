import os
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_ID: str = "artdrive1208"
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str
    GEMINI_API_KEY: str | None = None
    GOOGLE_APPLICATION_CREDENTIALS: str | None = None
    
    # ARKO API (공공데이터포털)
    ARKO_API_KEY: str | None = None
    ARKO_SERVICE_KEY: str | None = None
    
    # MMCA API (한국문화정보원 KCISA)
    MMCA_RESIDENCY_SERVICE_KEY: str | None = None
    MMCA_COLLECTION_SERVICE_KEY: str | None = None
    
    # CORS Settings
    ALLOWED_ORIGINS: list[str] = [
        "https://artdrive1208.web.app",
        "https://argo.art",
        "http://localhost:5173",
        "http://localhost:3000"
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

@lru_cache()
def get_settings():
    return Settings()
