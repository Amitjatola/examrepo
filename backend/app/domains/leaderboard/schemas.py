"""Pydantic schemas for leaderboard API."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class LeaderboardEntry(BaseModel):
    rank: int
    display_name: str
    is_current_user: bool = False
    questions_solved: int = Field(description="Distinct questions with at least one correct attempt")
    accuracy_pct: float
    revision_streak: int
    composite_score: float


class LeaderboardResponse(BaseModel):
    entries: list[LeaderboardEntry]
    current_user_rank: Optional[int] = None

    current_user_percentile: Optional[float] = Field(
        default=None,
        description="Approximate top-X% (rank/total*100); lower rank = smaller number = better",
    )

    total_participants: int


class VisibilityUpdate(BaseModel):
    visibility: Literal["anonymous", "public"]


class LeaderboardUserInfo(BaseModel):
    visibility: str
    alias: str
