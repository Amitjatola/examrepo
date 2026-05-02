"""Trap / complexity_flags search requires auth + Pro."""
import pytest
from datetime import datetime, timedelta

from app.domains.auth.services import create_user, create_access_token
from app.domains.auth.schemas import UserCreate
from app.domains.subscriptions.service import SubscriptionService
from app.domains.subscriptions.models import SubscriptionType, SubscriptionStatus


@pytest.mark.asyncio
async def test_trap_search_anonymous_returns_401(async_client):
    r = await async_client.get(
        "/api/v1/search",
        params={"q": "test", "complexity_flags": "edge_case_scenario"},
    )
    assert r.status_code == 401
    assert "Sign in" in r.json().get("detail", "")


@pytest.mark.asyncio
async def test_trap_search_free_user_returns_403(async_client, session):
    user = await create_user(
        session,
        UserCreate(
            email="freesearch@example.com",
            password="password123",
            full_name="Free Search",
        ),
    )
    sub_svc = SubscriptionService(session)
    subscription = await sub_svc.get_user_subscription(user.id)
    subscription.trial_end_date = datetime.utcnow() - timedelta(days=1)
    subscription.trial_start_date = datetime.utcnow() - timedelta(days=8)
    subscription.subscription_type = SubscriptionType.FREE
    subscription.status = SubscriptionStatus.EXPIRED
    session.add(subscription)
    await session.commit()

    token = create_access_token({"sub": user.email})
    r = await async_client.get(
        "/api/v1/search",
        params={"q": "test", "complexity_flags": "edge_case_scenario"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 403
    assert "Pro" in r.json().get("detail", "")


@pytest.mark.asyncio
async def test_trap_search_trial_user_returns_200(async_client, session):
    user = await create_user(
        session,
        UserCreate(
            email="trialsearch@example.com",
            password="password123",
            full_name="Trial Search",
        ),
    )
    token = create_access_token({"sub": user.email})
    r = await async_client.get(
        "/api/v1/search",
        params={"q": "test", "complexity_flags": "edge_case_scenario"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "questions" in data
