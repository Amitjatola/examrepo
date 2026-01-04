"""Subscription models."""
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class SubscriptionType(str, Enum):
    """Subscription type enum."""
    FREE = "free"
    TRIAL = "trial"
    PREMIUM = "premium"


class SubscriptionStatus(str, Enum):
    """Subscription status enum."""
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class UserSubscription(SQLModel, table=True):
    """User subscription model."""
    __tablename__ = "user_subscriptions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    
    subscription_type: SubscriptionType = Field(default=SubscriptionType.FREE)
    status: SubscriptionStatus = Field(default=SubscriptionStatus.ACTIVE)
    
    # Trial dates
    trial_start_date: Optional[datetime] = None
    trial_end_date: Optional[datetime] = None
    
    # Premium dates
    premium_start_date: Optional[datetime] = None
    premium_end_date: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def is_premium_active(self) -> bool:
        """Check if user has active premium access (trial or paid)."""
        now = datetime.utcnow()
        
        # Check trial
        if self.subscription_type == SubscriptionType.TRIAL:
            if self.trial_end_date and now <= self.trial_end_date:
                return self.status == SubscriptionStatus.ACTIVE
        
        # Check premium
        if self.subscription_type == SubscriptionType.PREMIUM:
            if self.premium_end_date and now <= self.premium_end_date:
                return self.status == SubscriptionStatus.ACTIVE
            # If no end date, assume lifetime/active subscription
            if not self.premium_end_date:
                return self.status == SubscriptionStatus.ACTIVE
        
        return False

    def days_remaining(self) -> Optional[int]:
        """Get days remaining for current subscription."""
        now = datetime.utcnow()
        
        if self.subscription_type == SubscriptionType.TRIAL and self.trial_end_date:
            delta = self.trial_end_date - now
            return max(0, delta.days)
        
        if self.subscription_type == SubscriptionType.PREMIUM and self.premium_end_date:
            delta = self.premium_end_date - now
            return max(0, delta.days)
        
        return None

    @staticmethod
    def create_trial_subscription(user_id: UUID, trial_days: int = 7) -> "UserSubscription":
        """Create a new trial subscription for a user."""
        now = datetime.utcnow()
        return UserSubscription(
            user_id=user_id,
            subscription_type=SubscriptionType.TRIAL,
            status=SubscriptionStatus.ACTIVE,
            trial_start_date=now,
            trial_end_date=now + timedelta(days=trial_days)
        )
