from sqlalchemy import Column, String, Boolean, DateTime, func
from database import Base

class PromoCode(Base):
    __tablename__ = "promocodes"

    code = Column(String(64), primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # Добавляем индекс, так как мы часто будем фильтровать неиспользованные коды
    is_used = Column(Boolean, default=False, index=True) 
