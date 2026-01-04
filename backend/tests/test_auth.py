"""Tests for authentication flow."""
import pytest
from app.domains.auth.services import create_user, get_user_by_email, verify_password, create_access_token
from app.domains.auth.schemas import UserCreate


@pytest.mark.asyncio
async def test_user_registration_creates_trial(session):
    """Test that user registration automatically creates a trial subscription."""
    user_create = UserCreate(
        email="newuser@example.com",
        password="securepass123",
        full_name="New User"
    )
    
    user = await create_user(session, user_create)
    
    assert user is not None
    assert user.email == "newuser@example.com"
    assert user.full_name == "New User"
    
    # Verify subscription was created
    from app.domains.subscriptions.service import SubscriptionService
    service = SubscriptionService(session)
    subscription = await service.get_user_subscription(user.id)
    
    assert subscription is not None
    assert subscription.subscription_type.value == "trial"


@pytest.mark.asyncio
async def test_user_login_flow(session):
    """Test complete user login flow."""
    # Create user
    user_create = UserCreate(
        email="logintest@example.com",
        password="mypassword",
        full_name="Login Test"
    )
    user = await create_user(session, user_create)
    
    # Verify user can be retrieved by email
    retrieved_user = await get_user_by_email(session, "logintest@example.com")
    assert retrieved_user is not None
    assert retrieved_user.id == user.id
    
    # Verify password
    assert verify_password("mypassword", retrieved_user.hashed_password) is True
    assert verify_password("wrongpassword", retrieved_user.hashed_password) is False


@pytest.mark.asyncio
async def test_access_token_creation():
    """Test JWT access token creation."""
    token = create_access_token({"sub": "test@example.com"})
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


@pytest.mark.asyncio
async def test_duplicate_email_registration(session):
    """Test that duplicate email registration is handled."""
    user_create = UserCreate(
        email="duplicate@example.com",
        password="pass123",
        full_name="First User"
    )
    
    # Create first user
    await create_user(session, user_create)
    
    # Attempt to create duplicate
    user_create2 = UserCreate(
        email="duplicate@example.com",
        password="pass456",
        full_name="Second User"
    )
    
    # This should raise an exception (integrity error)
    with pytest.raises(Exception):
        await create_user(session, user_create2)
