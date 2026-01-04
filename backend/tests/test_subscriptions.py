"""Tests for subscription system."""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from app.domains.subscriptions.models import UserSubscription, SubscriptionType, SubscriptionStatus
from app.domains.subscriptions.service import SubscriptionService
from app.domains.auth.models import User
from app.domains.auth.services import create_user
from app.domains.auth.schemas import UserCreate


@pytest.mark.asyncio
async def test_create_trial_subscription(session):
    """Test creating a trial subscription for a new user."""
    # Create a test user
    user_create = UserCreate(
        email="test@example.com",
        password="testpass123",
        full_name="Test User"
    )
    user = await create_user(session, user_create)
    
    # Verify trial subscription was auto-created
    service = SubscriptionService(session)
    subscription = await service.get_user_subscription(user.id)
    
    assert subscription is not None
    assert subscription.subscription_type == SubscriptionType.TRIAL
    assert subscription.status == SubscriptionStatus.ACTIVE
    assert subscription.trial_start_date is not None
    assert subscription.trial_end_date is not None
    
    # Verify trial is 7 days
    trial_duration = (subscription.trial_end_date - subscription.trial_start_date).days
    assert trial_duration == 7


@pytest.mark.asyncio
async def test_trial_is_premium_active(session):
    """Test that active trial grants premium access."""
    user_id = uuid4()
    subscription = UserSubscription.create_trial_subscription(user_id, trial_days=7)
    session.add(subscription)
    await session.commit()
    
    assert subscription.is_premium_active() is True


@pytest.mark.asyncio
async def test_expired_trial_not_premium(session):
    """Test that expired trial does not grant premium access."""
    user_id = uuid4()
    
    # Create trial that expired yesterday
    subscription = UserSubscription(
        user_id=user_id,
        subscription_type=SubscriptionType.TRIAL,
        status=SubscriptionStatus.ACTIVE,
        trial_start_date=datetime.utcnow() - timedelta(days=8),
        trial_end_date=datetime.utcnow() - timedelta(days=1)
    )
    session.add(subscription)
    await session.commit()
    
    assert subscription.is_premium_active() is False


@pytest.mark.asyncio
async def test_days_remaining_calculation(session):
    """Test days remaining calculation for trial."""
    user_id = uuid4()
    
    # Create trial with 3 days remaining
    subscription = UserSubscription(
        user_id=user_id,
        subscription_type=SubscriptionType.TRIAL,
        status=SubscriptionStatus.ACTIVE,
        trial_start_date=datetime.utcnow() - timedelta(days=4),
        trial_end_date=datetime.utcnow() + timedelta(days=3)
    )
    session.add(subscription)
    await session.commit()
    
    days = subscription.days_remaining()
    assert days == 3


@pytest.mark.asyncio
async def test_subscription_expiration_check(session):
    """Test automatic expiration of trial subscriptions."""
    user_id = uuid4()
    
    # Create expired trial
    subscription = UserSubscription(
        user_id=user_id,
        subscription_type=SubscriptionType.TRIAL,
        status=SubscriptionStatus.ACTIVE,
        trial_start_date=datetime.utcnow() - timedelta(days=8),
        trial_end_date=datetime.utcnow() - timedelta(days=1)
    )
    session.add(subscription)
    await session.commit()
    
    # Run expiration check
    service = SubscriptionService(session)
    await service.check_and_expire_subscription(user_id)
    
    # Refresh subscription
    await session.refresh(subscription)
    
    assert subscription.status == SubscriptionStatus.EXPIRED
    assert subscription.subscription_type == SubscriptionType.FREE


@pytest.mark.asyncio
async def test_get_subscription_response(session):
    """Test getting subscription response with computed fields."""
    user_id = uuid4()
    subscription = UserSubscription.create_trial_subscription(user_id, trial_days=7)
    session.add(subscription)
    await session.commit()
    
    service = SubscriptionService(session)
    response = await service.get_subscription_response(user_id)
    
    assert response is not None
    assert response.is_premium is True
    assert response.trial_days_remaining is not None
    assert response.trial_days_remaining <= 7
    assert response.subscription_type == SubscriptionType.TRIAL
