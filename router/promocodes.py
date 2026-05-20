"""
routers/promocodes.py — Public HTTP endpoints for promo codes.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from schemas import GenerateResponse, CheckRequest, CheckResponse
from promocode_service import check_code, generate_code

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/generate",
    response_model=GenerateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a new promo code",
)
async def generate(session: AsyncSession = Depends(get_session)):
    # FIX (#8): generate_code now returns str directly — no more dict["code"].
    try:
        code = await generate_code(session)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    return GenerateResponse(code=code)


@router.post(
    "/check",
    response_model=CheckResponse,
    summary="Validate a promo code (marks it as used if valid)",
)
async def check(body: CheckRequest, session: AsyncSession = Depends(get_session)):
    is_valid, message = await check_code(session, body.code)
    return CheckResponse(code=body.code.upper(), valid=is_valid, message=message)