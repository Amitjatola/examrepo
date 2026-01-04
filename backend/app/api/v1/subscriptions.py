"""Subscription API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.domains.auth.deps import get_current_user
from app.domains.auth.models import User
from app.domains.subscriptions.service import SubscriptionService
from app.domains.subscriptions.schemas import SubscriptionResponse

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("/me", response_model=SubscriptionResponse)
async def get_my_subscription(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get current user's subscription status."""
    service = SubscriptionService(session)
    
    # Check and update expiration status
    await service.check_and_expire_subscription(current_user.id)
    
    # Get subscription
    subscription = await service.get_subscription_response(current_user.id)
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    return subscription
