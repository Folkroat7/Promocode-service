from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from schemas import CheckRequest, CheckResponse, GenerateResponse # Предположим, схемы тут
import promocode_service

router = APIRouter()

@router.post("/generate", response_model=GenerateResponse, status_code=status.HTTP_201_CREATED)
async def generate_new_promocode(session: AsyncSession = Depends(get_session)):
    """Эндпоинт для создания нового уникального промокода."""
    try:
        new_code = await promocode_service.generate_code(session)
        return GenerateResponse(code=new_code)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_AVAILABLE,
            detail=str(e)
        )

@router.get("/validate/{code}", response_model=CheckResponse)
async def validate_promo(code: str, session: AsyncSession = Depends(get_session)):
    """Просто проверить: существует ли код и можно ли его применить."""
    result = await promocode_service.check_code(session, code)
    return CheckResponse(
        code=code.upper(),
        is_valid=result.success,
        message=result.message
    )

@router.post("/apply", response_model=CheckResponse)
async def apply_promo(request: CheckRequest, session: AsyncSession = Depends(get_session)):
    """Применить (активировать) промокод."""
    result = await promocode_service.redeem_code(session, request.code)
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=result.message
        )
    return CheckResponse(
        code=request.code.upper(),
        is_valid=True,
        message=result.message
    )        
