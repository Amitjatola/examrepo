"""SM-2 inspired scheduling — pure functions, no I/O."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass
class ReviewResult:
    next_revision_at: datetime
    new_interval: float
    new_ease_factor: float
    new_streak: int


MAX_INTERVAL_DAYS = 180.0
MIN_EASE_FACTOR = 1.3


def quality_to_int(quality: str) -> int:
    q = (quality or "").lower().strip()
    if q == "again":
        return 1
    if q == "hard":
        return 3
    if q == "good":
        return 4
    if q == "easy":
        return 5
    raise ValueError(f"Unknown quality: {quality}")


def calculate_next_revision(
    quality: int,
    current_interval: float,
    ease_factor: float,
    revision_count: int,
    streak: int,
    difficulty: str = "medium",
    *,
    now: datetime | None = None,
) -> ReviewResult:
    """SM-2 inspired. quality 0-5; revision_count is count of completed reviews before this one."""
    if now is None:
        now = datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    diff_mult = {"easy": 1.3, "medium": 1.0, "hard": 0.8}
    multiplier = diff_mult.get((difficulty or "medium").lower(), 1.0)

    if quality < 3:
        new_interval = 1.0
        new_ease = max(MIN_EASE_FACTOR, ease_factor - 0.2)
        new_streak = 0
    else:
        new_streak = streak + 1
        new_ease = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        new_ease = max(MIN_EASE_FACTOR, new_ease)

        if revision_count == 0:
            new_interval = 1.0
        elif revision_count == 1:
            new_interval = 3.0
        else:
            new_interval = current_interval * new_ease * multiplier

        new_interval = min(new_interval, MAX_INTERVAL_DAYS)

    next_at = now + timedelta(days=new_interval)

    return ReviewResult(
        next_revision_at=next_at,
        new_interval=round(new_interval, 2),
        new_ease_factor=round(new_ease, 4),
        new_streak=new_streak,
    )
