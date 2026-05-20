"""
database.py — SQLAlchemy async engine + session factory.
 
FIX (#5): init_db() now has explicit error handling for connection failures
at startup, with a clear log message instead of a raw traceback.
"""
 
import logging
 
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
 
from config import settings
from typing import AsyncGenerator
 
logger = logging.getLogger(__name__)
 
engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
 
 
class Base(DeclarativeBase):
    pass
 
 
async def init_db() -> None:
    """
    Create all tables on startup if they don't exist.
 
    FIX (#5): wraps the connection attempt so a Postgres outage at startup
    produces a readable error log instead of a raw SQLAlchemy traceback.
 
    NOTE (#7): replace create_all with Alembic before going to production.
    create_all is fine for dev but has no migration history — schema changes
    require manual intervention. Alembic handles this with versioned scripts.
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables verified / created.")
    except OperationalError as exc:
        # Log clearly and re-raise — the app should not start without a DB.
        logger.critical(
            "Cannot connect to the database at startup. "
            "Check POSTGRES_HOST / POSTGRES_PORT / credentials. Error: %s", exc
        )
        raise
 
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency — one session per request, closed automatically.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise