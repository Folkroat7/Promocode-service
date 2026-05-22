"""
config.py — Centralised configuration via pydantic-settings.

In Docker: vars injected via docker-compose environment: or --env-file.
Locally:   create a .env file (see .env.example).
Prod:      inject from your secrets manager (Vault, AWS SSM, etc.).
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- PostgreSQL ---
    POSTGRES_USER:     str = "postgres"
    POSTGRES_PASSWORD: str = "911734"
    POSTGRES_DB:       str = "promodb"
    POSTGRES_HOST:     str = "localhost"
    POSTGRES_PORT:     int = 5433

    @property
    def DATABASE_URL(self) -> str:
        u, pw, h, p, db = (
            self.POSTGRES_USER, self.POSTGRES_PASSWORD,
            self.POSTGRES_HOST, self.POSTGRES_PORT, self.POSTGRES_DB,
        )
        return f"postgresql+asyncpg://{u}:{pw}@{h}:{p}/{db}"

    # --- Code generation ---
    CODE_LENGTH:   int = 8
    CODE_PREFIX:   str = "PROMO"
    CODE_ALPHABET: str = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

    # --- CORS ---
    # FIX (#4): default is localhost-only, not "*".
    # [CHANGE FOR PRODUCTION]: set this in your .env file:
    #   CORS_ORIGINS=["https://yourdomain.com","https://admin.yourdomain.com"]
    # Never use ["*"] in production — it allows any website to call your API.
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # --- Admin ---
    # [CHANGE FOR PRODUCTION]: generate with:
    #   python -c "import secrets; print(secrets.token_hex(32))"
    ADMIN_API_KEY: str = "change-me-before-deploy"

    # --- Logging ---
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()