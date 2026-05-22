from dataclasses import dataclass
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import PromoCode
import logging

@dataclass
class ServiceResult:
    success: bool
    message: str
    promo: PromoCode = None

async def check_code(session: AsyncSession, code: str) -> ServiceResult:
    """Только проверяет существование и валидность, не 'сжигая' промокод."""
    stmt = select(PromoCode).where(PromoCode.code == code.upper())
    result = await session.execute(stmt)
    promo = result.scalar_one_or_none()

    if not promo:
        return ServiceResult(False, "Промокод не найден")
    if promo.is_used:
        return ServiceResult(False, "Промокод уже использован")
    
    return ServiceResult(True, "Промокод валиден", promo)

async def redeem_code(session: AsyncSession, code: str) -> ServiceResult:
    """Атомарно проверяет и помечает промокод как использованный."""
    # .with_for_update() блокирует строку до конца транзакции (commit)
    stmt = select(PromoCode).where(PromoCode.code == code.upper()).with_for_update()
    result = await session.execute(stmt)
    promo = result.scalar_one_or_none()

    if not promo:
        return ServiceResult(False, "Промокод не найден")
    
    if promo.is_used:
        # Даже если два запроса пришли одновременно, второй увидит True 
        # благодаря блокировке первого запроса
        return ServiceResult(False, "Промокод уже был использован")

    promo.is_used = True
    await session.commit() # Блокировка снимется здесь
    
    logging.info(f"Промокод {code} успешно активирован")
    return ServiceResult(True, "Промокод успешно активирован", promo)
        return False, "Code has already been used."

    # Valid — consume it so it cannot be reused.
    await mark_used(session, code)
    logger.info("Code redeemed successfully: %s", code)
    return True, "Code is valid and has been redeemed."
