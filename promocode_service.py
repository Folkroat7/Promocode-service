"""
services/promocode_service.py — Business logic layer.

Rules:
  • No FastAPI imports — plain Python only.
  • Raises standard exceptions; the router maps them to HTTP errors.
  • Returns str or tuple — never dicts, never ORM objects.
    Keeps the contract explicit and easy to test.
"""

import logging
import secrets

from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from store import get, mark_used, save

logger = logging.getLogger(__name__)


async def generate_code(session: AsyncSession) -> str:
    """
    Generate a unique promo code, persist it, and return the code string.

    FIX (#8): was returning dict{"code":..., "created_at":...}.
    The router only ever used ["code"], so returning str is cleaner
    and makes the contract explicit — callers know exactly what they get.
    """
    for attempt in range(10):
        raw = "".join(
            secrets.choice(settings.CODE_ALPHABET)
            for _ in range(settings.CODE_LENGTH)
        )
        code = f"{settings.CODE_PREFIX}-{raw}" if settings.CODE_PREFIX else raw

        if await get(session, code) is None:
            await save(session, code)
            logger.info("Generated code %s on attempt %d", code, attempt + 1)
            return code

    # This is astronomically unlikely with CODE_LENGTH >= 6,
    # but we log it as an error if it somehow happens.
    logger.error("Failed to generate a unique code after 10 attempts")
    raise RuntimeError("Could not generate a unique code after 10 attempts")


async def check_code(session: AsyncSession, raw_code: str) -> tuple[bool, str]:
    """
    Validate a promo code and mark it used if valid.

    FIX (#1, #3): mark_used is now called here — a valid code is consumed
    on first successful check. Without this call, is_used was checked but
    never set, making the field pointless.

    Returns (is_valid, human_readable_message).
    """
    code = raw_code.strip().upper()
    record = await get(session, code)

    if record is None:
        logger.info("Check failed — code not found: %s", code)
        return False, "Code not found."

    if record.is_used:
        logger.info("Check failed — code already used: %s", code)
        return False, "Code has already been used."

    # Valid — consume it so it cannot be reused.
    await mark_used(session, code)
    logger.info("Code redeemed successfully: %s", code)
    return True, "Code is valid and has been redeemed."