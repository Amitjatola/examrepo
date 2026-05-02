"""API tests for /api/v1/users/me/bookmarks."""
import uuid

import pytest

from app.domains.auth.services import create_user, create_access_token
from app.domains.auth.schemas import UserCreate
from app.domains.questions.models import Question


def _unique_email(prefix: str = "bm") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}@example.com"


def _minimal_question() -> Question:
    suffix = uuid.uuid4().hex[:10]
    return Question(
        question_id=f"PYTEST_BM_{suffix}",
        exam_name="GATE",
        subject="Aerospace Engineering",
        year=2099,
        question_number=1,
        question_text="Pytest bookmark question",
        question_type="MCQ",
        marks=1.0,
        negative_marks=0.33,
        options={"A": "1", "B": "2"},
        answer_key="A",
    )


@pytest.mark.asyncio
async def test_bookmarks_list_requires_auth(async_client):
    response = await async_client.get("/api/v1/users/me/bookmarks")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_bookmark_upsert_get_list_delete_flow(async_client, session):
    user = await create_user(
        session,
        UserCreate(email=_unique_email(), password="password123", full_name="Bookmark User"),
    )
    q = _minimal_question()
    session.add(q)
    await session.commit()
    await session.refresh(q)

    token = create_access_token({"sub": user.email})
    headers = {"Authorization": f"Bearer {token}"}

    put = await async_client.put(
        f"/api/v1/users/me/bookmarks/{q.question_id}",
        json={"note": "unit test note", "is_bookmarked": True},
        headers=headers,
    )
    assert put.status_code == 200
    body = put.json()
    assert body["question_id"] == q.question_id
    assert body["note"] == "unit test note"
    assert body["is_bookmarked"] is True

    one = await async_client.get(
        f"/api/v1/users/me/bookmarks/{q.question_id}",
        headers=headers,
    )
    assert one.status_code == 200
    assert one.json()["note"] == "unit test note"

    listed = await async_client.get("/api/v1/users/me/bookmarks", headers=headers)
    assert listed.status_code == 200
    items = listed.json()
    assert isinstance(items, list)
    assert any(item.get("question_id") == q.question_id for item in items)

    deleted = await async_client.delete(
        f"/api/v1/users/me/bookmarks/{q.question_id}",
        headers=headers,
    )
    assert deleted.status_code == 200
    assert deleted.json().get("deleted") is True

    missing = await async_client.get(
        f"/api/v1/users/me/bookmarks/{q.question_id}",
        headers=headers,
    )
    assert missing.status_code == 404
