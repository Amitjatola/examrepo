"""Subscription service."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from .models import UserSubscription, SubscriptionType, SubscriptionStatus
from .schemas import SubscriptionResponse


class SubscriptionService:
    """Service for managing user subscriptions."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_subscription(self, user_id: UUID) -> Optional[UserSubscription]:
        """Get user's subscription."""
        statement = select(UserSubscription).where(UserSubscription.user_id == user_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def create_trial_subscription(self, user_id: UUID, trial_days: int = 7) -> UserSubscription:
        """Create a trial subscription for a new user."""
        subscription = UserSubscription.create_trial_subscription(user_id, trial_days)
        self.session.add(subscription)
        await self.session.commit()
        await self.session.refresh(subscription)
        return subscription

    async def get_subscription_response(self, user_id: UUID) -> Optional[SubscriptionResponse]:
        """Get subscription with computed fields for API response."""
        subscription = await self.get_user_subscription(user_id)
        if not subscription:
            return None

        # Compute is_premium and days_remaining
        is_premium = subscription.is_premium_active()
        trial_days = None
        premium_days = None

        if subscription.subscription_type == SubscriptionType.TRIAL:
            trial_days = subscription.days_remaining()
        elif subscription.subscription_type == SubscriptionType.PREMIUM:
            premium_days = subscription.days_remaining()

        return SubscriptionResponse(
            id=subscription.id,
            user_id=subscription.user_id,
            subscription_type=subscription.subscription_type,
            status=subscription.status,
            is_premium=is_premium,
            trial_days_remaining=trial_days,
            premium_days_remaining=premium_days,
            trial_start_date=subscription.trial_start_date,
            trial_end_date=subscription.trial_end_date,
            premium_start_date=subscription.premium_start_date,
            premium_end_date=subscription.premium_end_date,
            created_at=subscription.created_at,
            updated_at=subscription.updated_at
        )

    async def check_and_expire_subscription(self, user_id: UUID) -> None:
        """Check if subscription has expired and update status."""
        subscription = await self.get_user_subscription(user_id)
        if not subscription:
            return

        now = datetime.utcnow()

        # Check trial expiration
        if subscription.subscription_type == SubscriptionType.TRIAL:
            if subscription.trial_end_date and now > subscription.trial_end_date:
                subscription.status = SubscriptionStatus.EXPIRED
                subscription.subscription_type = SubscriptionType.FREE
                subscription.updated_at = now
                self.session.add(subscription)
                await self.session.commit()

        # Check premium expiration
        elif subscription.subscription_type == SubscriptionType.PREMIUM:
            if subscription.premium_end_date and now > subscription.premium_end_date:
                subscription.status = SubscriptionStatus.EXPIRED
                subscription.subscription_type = SubscriptionType.FREE
                subscription.updated_at = now
                self.session.add(subscription)
                await self.session.commit()
