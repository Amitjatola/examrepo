"""User question revision scheduling (SM-2)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, UniqueConstraint, Index
from sqlalchemy.sql import func
from sqlmodel import Field, SQLModel


class UserQuestionRevision(SQLModel, table=True):
    __tablename__ = "user_question_revision"
    __table_args__ = (
        UniqueConstraint("user_id", "question_uuid", name="uq_user_question_revision"),
        Index("idx_next_revision_user", "user_id", "next_revision_at"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    question_uuid: uuid.UUID = Field(foreign_key="questions.id", index=True)

    last_attempted_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    last_result: Optional[str] = Field(default=None, max_length=20)
    revision_count: int = Field(default=0)
    interval_days: float = Field(default=1.0)
    next_revision_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    ease_factor: float = Field(default=2.5)
    difficulty: str = Field(default="medium", max_length=10)
    streak: int = Field(default=0)

    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now()),
    )
