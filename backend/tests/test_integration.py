"""Integration tests for complete user flows."""
import pytest
from datetime import datetime, timedelta

from app.domains.auth.services import create_user
from app.domains.auth.schemas import UserCreate
from app.domains.subscriptions.service import SubscriptionService
from app.domains.subscriptions.models import SubscriptionType, SubscriptionStatus


@pytest.mark.asyncio
async def test_complete_new_user_flow(session):
    """Test complete flow: signup -> trial created -> premium access granted."""
    # Step 1: User signs up
    user_create = UserCreate(
        email="complete@example.com",
        password="password123",
        full_name="Complete Test"
    )
    user = await create_user(session, user_create)
    
    # Step 2: Verify trial subscription exists
    service = SubscriptionService(session)
    subscription = await service.get_user_subscription(user.id)
    
    assert subscription is not None
    assert subscription.subscription_type == SubscriptionType.TRIAL
    
    # Step 3: Verify premium access is granted
    assert subscription.is_premium_active() is True
    
    # Step 4: Get subscription response (as API would return)
    response = await service.get_subscription_response(user.id)
    
    assert response.is_premium is True
    assert response.trial_days_remaining is not None
    assert response.trial_days_remaining <= 7
    assert response.trial_days_remaining >= 0


@pytest.mark.asyncio
async def test_trial_expiration_flow(session):
    """Test flow: trial expires -> premium access revoked -> downgrade to free."""
    # Create user with expired trial
    user_create = UserCreate(
        email="expired@example.com",
        password="password123",
        full_name="Expired Test"
    )
    user = await create_user(session, user_create)
    
    # Manually expire the trial
    service = SubscriptionService(session)
    subscription = await service.get_user_subscription(user.id)
    
    # Set trial to expired (8 days ago)
    subscription.trial_start_date = datetime.utcnow() - timedelta(days=8)
    subscription.trial_end_date = datetime.utcnow() - timedelta(days=1)
    session.add(subscription)
    await session.commit()
    
    # Run expiration check
    await service.check_and_expire_subscription(user.id)
    
    # Verify subscription was downgraded
    await session.refresh(subscription)
    assert subscription.status == SubscriptionStatus.EXPIRED
    assert subscription.subscription_type == SubscriptionType.FREE
    assert subscription.is_premium_active() is False
    
    # Verify API response
    response = await service.get_subscription_response(user.id)
    assert response.is_premium is False


@pytest.mark.asyncio
async def test_premium_access_control_logic(session):
    """Test premium access control for different subscription states."""
    # Test 1: Active trial = premium access
    user1 = await create_user(session, UserCreate(
        email="trial@test.com",
        password="pass",
        full_name="Trial User"
    ))
    service = SubscriptionService(session)
    sub1 = await service.get_user_subscription(user1.id)
    assert sub1.is_premium_active() is True
    
    # Test 2: Expired trial = no premium access
    sub1.trial_end_date = datetime.utcnow() - timedelta(days=1)
    session.add(sub1)
    await session.commit()
    await session.refresh(sub1)
    assert sub1.is_premium_active() is False
    
    # Test 3: Free tier = no premium access
    sub1.subscription_type = SubscriptionType.FREE
    session.add(sub1)
    await session.commit()
    await session.refresh(sub1)
    assert sub1.is_premium_active() is False
