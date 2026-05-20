"""
main.py — App wiring.
 
FIX (#6): logging is configured here at startup, once, for the whole app.
Every module gets its own logger via logging.getLogger(__name__) —
they all inherit the level and handler set here.
"""
 
import logging
import logging.config
from contextlib import asynccontextmanager
 
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
 
from config import settings
from database import init_db
from router import promocodes
from router import admin
 
 
def setup_logging() -> None:
    """
    Configure stdlib logging for the whole application.
 
    Format: timestamp | level | module name | message
    This format makes it easy to grep by module in production log aggregators
    (Datadog, CloudWatch, etc.).
 
    LOG_LEVEL is read from config so you can set DEBUG in dev, INFO/WARNING in prod.
    """
    logging.basicConfig(
        level=settings.LOG_LEVEL.upper(),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    # Quieten SQLAlchemy's verbose connection pool logs unless we're in DEBUG.
    if settings.LOG_LEVEL.upper() != "DEBUG":
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
 
 
@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting PromoCode API...")
    await init_db()
    logger.info("Startup complete.")
    yield
    logger.info("Shutting down.")
 
 
app = FastAPI(
    title="PromoCode API",
    version="1.0.0",
    lifespan=lifespan,
)
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
app.include_router(promocodes.router, prefix="/api/v1/promocodes", tags=["promocodes"])
app.include_router(admin.router,      prefix="/api/v1/admin",      tags=["admin"])
 
 
@app.get("/health", tags=["meta"])
async def health():
    return {"status": "ok"}
  