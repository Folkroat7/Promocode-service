"""
schemas.py — Pydantic models for request / response bodies.

Why separate schemas from DB models?
  • Your DB model (what's stored) and your API contract (what's exposed)
    often differ — e.g. you never want to leak internal IDs or timestamps.
  • Validation and serialisation logic lives in one place.
  • Swagger / OpenAPI docs are generated automatically from these models.
"""

from datetime import datetime
from pydantic import BaseModel, Field


# ── Responses ──────────────────────────────────────────────────────────────

class PromoCodeOut(BaseModel):
    """Shape of a promo code returned to the client."""
    code: str
    created_at: datetime
    is_used: bool

    # Tells Pydantic to read attributes from ORM objects, not just dicts.
    # Remove this if you're not using SQLAlchemy / Tortoise ORM.
    model_config = {"from_attributes": True}


class GenerateResponse(BaseModel):
    code: str
    message: str = "Code generated successfully"


class CheckResponse(BaseModel):
    code: str
    valid: bool        # True  → code exists and has not been used
    message: str       # Human-readable status for the UI


# ── Requests ───────────────────────────────────────────────────────────────

class CheckRequest(BaseModel):
    code: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="The promo code to validate",
    )