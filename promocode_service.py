from dataclasses import dataclass
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import PromoCode
import logging
import secrets

@dataclass
class ServiceResult:
    success: bool
    message: str
    promo: PromoCode = None

async def generate_code(session: AsyncSession, prefix: str = "PROMO-") -> str:
    """Генерирует случайный код и проверяет его уникальность в БД."""
    
    for _ in range(10): 
        raw_code = secrets.token_hex(4).upper()
        full_code = f"{prefix}{raw_code}"
        
        stmt = select(PromoCode).where(PromoCode.code == full_code)
        result = await session.execute(stmt)
        if result.scalar_one_or_none() is None:
            new_promo = PromoCode(code=full_code)
            session.add(new_promo)
            await session.commit()
            return full_code
            
    raise RuntimeError("Не удалось сгенерировать уникальный код. База переполнена?")

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
    stmt = select(PromoCode).where(PromoCode.code == code.upper()).with_for_update()
    result = await session.execute(stmt)
    promo = result.scalar_one_or_none()

    if not promo:
        return ServiceResult(False, "Промокод не найден")
    
    if promo.is_used:
        return ServiceResult(False, "Промокод уже был использован")

    promo.is_used = True
    await session.commit() 
    
    logging.info(f"Промокод {code} успешно активирован")
    return ServiceResult(True, "Промокод успешно активирован", promo)

