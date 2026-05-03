"""Pydantic schemas for revision APIs."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class RevisionAdd(BaseModel):
    question_id: str = Field(..., description="Public question id e.g. GATE_AE_2008_Q01")
    difficulty: Literal["easy", "medium", "hard"] = "medium"


class RevisionAnswer(BaseModel):
    quality: Literal["again", "hard", "good", "easy"]


class RevisionResponse(BaseModel):
    id: int
    user_id: int
    question_uuid: uuid.UUID
    question_id_str: str
    last_attempted_at: Optional[datetime] = None
    last_result: Optional[str] = None
    revision_count: int
    interval_days: float
    next_revision_at: datetime
    ease_factor: float
    difficulty: str
    streak: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    days_overdue: float = Field(
        0.0,
        description="Days past next_revision_at when snapshot was taken (0 if not overdue)",
    )

    class Config:
        from_attributes = True


class RevisionQueueItem(BaseModel):
    """One due row + minimal question fields for list UI."""

    revision: RevisionResponse
    question_text_preview: str = ""
    subject: str = ""
    year: int = 0
    question_number: int = 0
    topic_tag: Optional[str] = None


class RevisionQueueResponse(BaseModel):
    total_due: int
    items: list[RevisionQueueItem]


class MasteryDistribution(BaseModel):
    new: int
    learning: int
    mature: int


class RevisionStatsResponse(BaseModel):
    due_today: int
    due_this_week: int
    total_tracked: int
    current_streak: int
    mastery: MasteryDistribution


class HistoryDay(BaseModel):
    date: str
    count: int
