"""
store.py — Data access layer (repository pattern).

Rules:
  • Only this file imports SQLAlchemy query constructs.
  • Returns ORM objects or None — never HTTP responses, never dicts.
  • All functions are async because the DB driver (asyncpg) is async.

Every function is actually called by the service layer:
  save      ← generate_code
  get       ← check_code, generate_code (collision check)
  mark_used ← check_code (marks code consumed on valid check)
  all_codes ← admin router GET /admin/codes
"""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import PromoCode

logger = logging.getLogger(__name__)


async def save(session: AsyncSession, code: str) -> PromoCode:
    """Insert a new promo code row and return the ORM object."""
    record = PromoCode(code=code)
    session.add(record)
    await session.commit()
    await session.refresh(record)  # reload DB-generated defaults (created_at)
    logger.info("Saved new code: %s", code)
    return record


async def get(session: AsyncSession, code: str) -> PromoCode | None:
    """Fetch one code by primary key (case-insensitive). Returns None if not found."""
    return await session.get(PromoCode, code.upper())


async def mark_used(session: AsyncSession, code: str) -> None:
    """
    Flip is_used=True for an existing code.
    Called by check_code after a successful validation so each code
    can only be redeemed once.
    """
    record = await get(session, code)
    if record:
        record.is_used = True
        await session.commit()
        logger.info("Marked code as used: %s", code)


async def all_codes(session: AsyncSession) -> list[PromoCode]:
    """
    Return every stored code, newest first.
    Used by the admin router — not exposed publicly.
    """
    result = await session.execute(
        select(PromoCode).order_by(PromoCode.created_at.desc())
    )
    return list(result.scalars().all())