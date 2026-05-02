"""Tests for extended dashboard statistics (/dashboard/stats)."""
import uuid

import pytest

from app.domains.auth.services import create_user, create_access_token
from app.domains.auth.schemas import UserCreate
from app.domains.questions.models import Question, UserAttempt
from app.domains.questions.service import QuestionService


def _unique_email(prefix: str = "dash") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}@example.com"


def _minimal_question(*, topic_name: str = "StatsTopic") -> Question:
    suffix = uuid.uuid4().hex[:10]
    return Question(
        question_id=f"PYTEST_STAT_{suffix}",
        exam_name="GATE",
        subject="Aerospace Engineering",
        year=2099,
        question_number=1,
        question_text="Pytest dashboard stats question",
        question_type="MCQ",
        marks=1.0,
        negative_marks=0.33,
        options={"A": "1", "B": "2"},
        answer_key="A",
        tier_1_core_research={
            "hierarchical_tags": {
                "topic": {"name": topic_name},
                "concepts": [{"name": "ConceptA"}],
            }
        },
    )


@pytest.mark.asyncio
async def test_get_user_dashboard_stats_aggregates_attempts(session):
    user = await create_user(
        session,
        UserCreate(email=_unique_email(), password="password123", full_name="Dashboard Stats"),
    )
    q = _minimal_question()
    session.add(q)
    await session.commit()
    await session.refresh(q)

    session.add(
        UserAttempt(
            user_id=user.id,
            question_id=q.id,
            is_correct=True,
            time_taken_seconds=100,
        )
    )
    session.add(
        UserAttempt(
            user_id=user.id,
            question_id=q.id,
            is_correct=False,
            time_taken_seconds=20,
        )
    )
    await session.commit()

    svc = QuestionService(session)
    stats = await svc.get_user_dashboard_stats(user.id)

    assert stats.attempt_accuracy_pct == 50.0
    assert stats.topic_avg_time_seconds.get("StatsTopic") == 60.0
    assert stats.questions_attempted == 1
    assert isinstance(stats.topic_avg_time_seconds, dict)
    assert isinstance(stats.readiness_score, float)
    assert isinstance(stats.syllabus_topic_catalog_total, int)
    assert stats.syllabus_topic_catalog_total >= 1
    assert 0.0 <= stats.syllabus_progress <= 100.0
    assert 0.0 <= stats.readiness_score <= 100.0


@pytest.mark.asyncio
async def test_dashboard_stats_api_returns_extended_fields(async_client, session):
    user = await create_user(
        session,
        UserCreate(email=_unique_email("api"), password="password123", full_name="Dashboard API"),
    )
    token = create_access_token({"sub": user.email})
    response = await async_client.get(
        "/api/v1/dashboard/stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    for key in (
        "topic_avg_time_seconds",
        "attempt_accuracy_pct",
        "readiness_score",
        "syllabus_topic_catalog_total",
        "syllabus_progress",
        "questions_attempted",
    ):
        assert key in data


@pytest.mark.asyncio
async def test_dashboard_stats_requires_auth(async_client):
    response = await async_client.get("/api/v1/dashboard/stats")
    assert response.status_code == 401
