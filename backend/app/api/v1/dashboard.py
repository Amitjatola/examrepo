from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.domains.questions.service import QuestionService
from app.domains.questions.schemas import DashboardStats
from app.domains.questions.schemas import DashboardStats
from app.domains.auth.deps import get_current_user
from app.domains.auth.models import User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Get dashboard statistics for the current user.
    """
    service = QuestionService(session)
    stats = await service.get_user_dashboard_stats(current_user.id)
    return stats
