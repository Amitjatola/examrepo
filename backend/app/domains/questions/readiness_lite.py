"""Pure helpers for dashboard \"readiness lite\" (additive index, gap, days heuristic)."""

from __future__ import annotations

import math
from typing import TypedDict

TARGET_READINESS_BY_BAND: dict[str, float] = {
    "qualifying": 55.0,
    "good": 70.0,
    "ranker": 85.0,
}


def target_readiness_for_band(target_band: str) -> float:
    key = (target_band or "good").lower().strip()
    return TARGET_READINESS_BY_BAND.get(key, TARGET_READINESS_BY_BAND["good"])


class ReadinessLiteComputed(TypedDict):
    readiness_lite_pct: float
    target_readiness_pct: float
    cutoff_gap_pct: float
    days_to_target_estimate: int


def compute_readiness_lite(
    attempt_accuracy_pct: float,
    syllabus_progress: float,
    target_band: str,
    attempts_last_7_days: int,
) -> ReadinessLiteComputed:
    readiness_lite_pct = round(0.5 * attempt_accuracy_pct + 0.5 * syllabus_progress, 1)
    target_readiness_pct = target_readiness_for_band(target_band)
    cutoff_gap_pct = round(float(target_readiness_pct) - readiness_lite_pct, 1)
    attempts_per_day = attempts_last_7_days / 7.0
    if cutoff_gap_pct <= 0:
        days_to_target_estimate = 0
    else:
        daily_gain_pct = min(2.0, 0.15 * attempts_per_day)
        days_to_target_estimate = int(math.ceil(cutoff_gap_pct / max(daily_gain_pct, 0.05)))
    return ReadinessLiteComputed(
        readiness_lite_pct=readiness_lite_pct,
        target_readiness_pct=float(target_readiness_pct),
        cutoff_gap_pct=cutoff_gap_pct,
        days_to_target_estimate=days_to_target_estimate,
    )
