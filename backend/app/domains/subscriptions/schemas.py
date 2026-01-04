"""Subscription schemas."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from .models import SubscriptionType, SubscriptionStatus


class SubscriptionResponse(BaseModel):
    """Subscription response schema."""
    id: UUID
    user_id: UUID
    subscription_type: SubscriptionType
    status: SubscriptionStatus
    is_premium: bool
    trial_days_remaining: Optional[int] = None
    premium_days_remaining: Optional[int] = None
    trial_start_date: Optional[datetime] = None
    trial_end_date: Optional[datetime] = None
    premium_start_date: Optional[datetime] = None
    premium_end_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubscriptionCreate(BaseModel):
    """Schema for creating subscriptions (admin/webhook use)."""
    user_id: UUID
    subscription_type: SubscriptionType
    premium_days: Optional[int] = None  # For premium subscriptions
