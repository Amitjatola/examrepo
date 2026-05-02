from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.domains.questions.service import QuestionService
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


@router.get("/weak-topics")
async def get_weak_topics(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Topics ordered by lowest accuracy first (for drill / coach UIs).
    Uses the same aggregation as /dashboard/stats topic_performance.
    """
    service = QuestionService(session)
    stats = await service.get_user_dashboard_stats(current_user.id)
    ranked = sorted(stats.topic_performance.items(), key=lambda x: (x[1], x[0]))[:25]
    return {
        "topics": [{"topic": name, "accuracy_pct": acc} for name, acc in ranked],
    }


@router.get("/remediation")
async def get_remediation_queue(
    limit: int = Query(25, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Recent distinct questions the user answered incorrectly (for review playlists)."""
    service = QuestionService(session)
    items = await service.get_remediation_question_ids(current_user.id, limit)
    return {"items": items}
