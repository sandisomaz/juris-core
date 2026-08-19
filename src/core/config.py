import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "JurisCore"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8888
    HOST: str = "0.0.0.0"

    DATABASE_URL: str = "sqlite+aiosqlite:///./juris_core.db"
    DB_ECHO: bool = False

    SECRET_KEY: str = os.getenv("SECRET_KEY", os.getenv("JURISCORE_SECRET_KEY", ""))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:8888",
        "http://127.0.0.1:8888",
        "http://localhost:3000",
        "http://localhost:5173"
    ]

    LLM_MODE: str = "local"
    LLM_MODEL: str = "qwen2.5:3b"
    OLLAMA_HOST: str = "http://127.0.0.1:11434"
    LLM_REQUEST_TIMEOUT_SECONDS: int = 600
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def __init__(self, **values):
        import secrets
        super().__init__(**values)
        if not self.SECRET_KEY:
            # Ephemeral cryptographically random secret if none provided in environment
            self.SECRET_KEY = secrets.token_hex(32)


settings = Settings()
