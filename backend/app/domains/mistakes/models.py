"""Per-user mistake annotation overlay on UserAttempt."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Text, UniqueConstraint
from sqlalchemy.sql import func
from sqlmodel import Field, SQLModel


class UserMistakeAnnotation(SQLModel, table=True):
    __tablename__ = "user_mistake_annotations"
    __table_args__ = (
        UniqueConstraint("user_id", "question_uuid", name="uq_user_mistake_annotation"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    question_uuid: uuid.UUID = Field(foreign_key="questions.id", index=True)

    error_type: Optional[str] = Field(default=None, max_length=20)
    wrong_count: int = Field(default=0)
    correct_count: int = Field(default=0)

    last_wrong_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    last_correct_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    is_resolved: bool = Field(default=False)
    notes: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))

    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now()),
    )
