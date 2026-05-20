"""
models.py — SQLAlchemy ORM table definitions.

One class = one table.
Keep models free of business logic — that lives in services/.
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class PromoCode(Base):
    __tablename__ = "promo_codes"

    code:       Mapped[str]      = mapped_column(String(64), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    is_used:    Mapped[bool]     = mapped_column(Boolean, default=False)