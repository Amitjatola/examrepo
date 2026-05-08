"""Leaderboard API (privacy-aware)."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.domains.auth.deps import get_current_user
from app.domains.auth.models import User
from app.domains.leaderboard.schemas import (
    LeaderboardResponse,
    LeaderboardUserInfo,
    VisibilityUpdate,
)
from app.domains.leaderboard.service import LeaderboardService

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("", response_model=LeaderboardResponse)
async def get_leaderboard(
    sort_by: str = Query("composite"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if sort_by not in ("composite", "accuracy", "questions_solved"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sort_by must be composite, accuracy, or questions_solved",
        )
    svc = LeaderboardService(session)
    return await svc.get_leaderboard(
        current_user.id,
        sort_by=sort_by,
        limit=limit,
        offset=offset,
    )


@router.get("/me", response_model=LeaderboardUserInfo)
async def get_my_leaderboard_settings(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    svc = LeaderboardService(session)
    info = await svc.get_user_leaderboard_info(current_user.id)
    if not info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return info


@router.patch("/visibility", response_model=LeaderboardUserInfo)
async def patch_leaderboard_visibility(
    body: VisibilityUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    svc = LeaderboardService(session)
    out = await svc.update_visibility(current_user.id, body.visibility)
    if not out:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return out
