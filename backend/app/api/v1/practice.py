"""Authenticated practice helpers (mock papers, etc.)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.domains.auth.deps import get_current_user
from app.domains.auth.models import User
from app.domains.questions.schemas import MockPaperRequest
from app.domains.questions.service import QuestionService
from app.domains.subscriptions.service import SubscriptionService

router = APIRouter(prefix="/practice", tags=["practice"])


@router.post("/mock-paper")
async def create_mock_paper(
    body: MockPaperRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Build an adaptive mock paper (weak topics + trap-heavy + random fill).
    Pro only — same policy as trap search.
    """
    sub_svc = SubscriptionService(session)
    if not await sub_svc.user_has_active_premium(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Adaptive mock papers are a Pro feature.",
        )
    svc = QuestionService(session)
    question_ids = await svc.build_mock_paper(current_user.id, body)
    if not question_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No questions available to build a mock paper.",
        )
    return {"question_ids": question_ids}
