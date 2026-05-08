import hashlib
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func

LEADERBOARD_ALIAS_SALT = "aerogate_lb_2026"


def generate_leaderboard_alias(user_id: int) -> str:
    """Stable anonymous handle: Learner_<4 hex chars from SHA256(salt:user_id)>."""
    digest = hashlib.sha256(f"{LEADERBOARD_ALIAS_SALT}:{user_id}".encode()).hexdigest()[:4].upper()
    return f"Learner_{digest}"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    email: str = Field(unique=True, index=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    full_name: Optional[str] = Field(default=None, nullable=True)
    is_active: bool = Field(default=True)
    leaderboard_alias: Optional[str] = Field(default=None, max_length=64, nullable=True)
    leaderboard_visibility: str = Field(default="anonymous", max_length=20)
    created_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )

