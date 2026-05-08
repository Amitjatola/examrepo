"""Unit tests for readiness_lite pure helpers."""

from app.domains.questions.readiness_lite import compute_readiness_lite, target_readiness_for_band


def test_target_readiness_for_band_maps_and_defaults_unknown():
    assert target_readiness_for_band("qualifying") == 55.0
    assert target_readiness_for_band("good") == 70.0
    assert target_readiness_for_band("ranker") == 85.0
    assert target_readiness_for_band("RANKER") == 85.0
    assert target_readiness_for_band("nope") == 70.0
    assert target_readiness_for_band("") == 70.0


def test_compute_readiness_lite_gap_non_positive_yields_zero_days():
    out = compute_readiness_lite(
        attempt_accuracy_pct=80.0,
        syllabus_progress=80.0,
        target_band="good",
        attempts_last_7_days=0,
    )
    assert out["readiness_lite_pct"] == 80.0
    assert out["target_readiness_pct"] == 70.0
    assert out["cutoff_gap_pct"] == -10.0
    assert out["days_to_target_estimate"] == 0


def test_compute_readiness_lite_zero_attempts_uses_floor_daily_gain():
    out = compute_readiness_lite(
        attempt_accuracy_pct=0.0,
        syllabus_progress=0.0,
        target_band="good",
        attempts_last_7_days=0,
    )
    assert out["readiness_lite_pct"] == 0.0
    assert out["cutoff_gap_pct"] == 70.0
    # daily_gain = min(2, 0) = 0 -> denom max(0.05) -> ceil(70/0.05) = 1400
    assert out["days_to_target_estimate"] == 1400


def test_compute_readiness_lite_pace_reduces_days():
    slow = compute_readiness_lite(50.0, 50.0, "ranker", attempts_last_7_days=7)
    fast = compute_readiness_lite(50.0, 50.0, "ranker", attempts_last_7_days=70)
    assert slow["cutoff_gap_pct"] == fast["cutoff_gap_pct"] == 35.0
    assert fast["days_to_target_estimate"] < slow["days_to_target_estimate"]
