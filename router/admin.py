"""
routers/admin.py — Internal admin endpoints.

FIX (#2): all_codes() from store.py is now actually called here.

Protected by a static API key in the X-Admin-Key header.
In production, use a proper auth system (OAuth2, JWT, etc.) —
a static key is fine for internal tooling but not for user-facing APIs.

[CHANGE FOR PRODUCTION]: set ADMIN_API_KEY to a long random secret.
  Generate one with: python -c "import secrets; print(secrets.token_hex(32))"
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import get_session
from schemas import PromoCodeOut
from store import all_codes

logger = logging.getLogger(__name__)
router = APIRouter()

# FastAPI reads this header from the incoming request automatically.
api_key_header = APIKeyHeader(name="X-Admin-Key", auto_error=False)


async def require_admin_key(key: str | None = Depends(api_key_header)):
    """
    Dependency — rejects any request where the header value doesn't
    match the configured ADMIN_API_KEY.
    auto_error=False means FastAPI won't 403 before we do — we return
    401 (not authenticated) vs 403 (authenticated but forbidden), which
    is the semantically correct distinction.
    """
    if key != settings.ADMIN_API_KEY:
        logger.warning("Admin access denied — bad or missing API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing admin API key.",
        )


@router.get(
    "/codes",
    response_model=list[PromoCodeOut],
    summary="List all promo codes (admin only)",
    dependencies=[Depends(require_admin_key)],
)
async def list_codes(session: AsyncSession = Depends(get_session)):
    """
    Returns all codes ordered newest-first.
    Requires X-Admin-Key header matching ADMIN_API_KEY in config.
    """
    codes = await all_codes(session)
    logger.info("Admin listed all codes — total: %d", len(codes))
    return codes