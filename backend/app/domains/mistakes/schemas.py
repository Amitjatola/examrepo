"""Pydantic schemas for Mistake Museum."""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class MistakeMuseumItem(BaseModel):
    question_id_str: str
    subject: str = ""
    year: int = 0
    question_number: int = 0
    topic_tag: Optional[str] = None
    question_text_preview: str = ""
    wrong_count: int = 0
    correct_count: int = 0
    error_type: Optional[str] = None
    is_resolved: bool = False
    last_wrong_at: Optional[datetime] = None
    last_correct_at: Optional[datetime] = None
    notes: Optional[str] = None
    improvement_pct: float = Field(0.0, description="correct / total * 100")
    in_revision: bool = False


class MistakeSummary(BaseModel):
    total_mistakes: int = 0
    resolved_count: int = 0
    conceptual_count: int = 0
    careless_count: int = 0
    tricky_count: int = 0
    untagged_count: int = 0
    top_weak_topics: list[dict] = Field(default_factory=list)


class MistakeMuseumResponse(BaseModel):
    total: int
    items: list[MistakeMuseumItem]
    summary: MistakeSummary


class MistakeAnnotationUpdate(BaseModel):
    error_type: Optional[Literal["conceptual", "careless", "tricky"]] = None
    is_resolved: Optional[bool] = None
    notes: Optional[str] = None


class RepeatOffenderItem(BaseModel):
    question_id_str: str
    wrong_count: int
    subject: str = ""
    topic_tag: Optional[str] = None
