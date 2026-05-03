"""Spaced repetition / revision tracking API."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.domains.auth.deps import get_current_user
from app.domains.auth.models import User
from app.domains.revisions.schemas import (
    HistoryDay,
    RevisionAdd,
    RevisionAnswer,
    RevisionQueueResponse,
    RevisionResponse,
    RevisionStatsResponse,
)
from app.domains.revisions.service import RevisionService

router = APIRouter(prefix="/revisions", tags=["revisions"])


@router.post("/add", response_model=RevisionResponse)
async def add_revision(
    body: RevisionAdd,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    svc = RevisionService(session)
    try:
        return await svc.add_to_revision(current_user.id, body.question_id, body.difficulty)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.get("/queue/today", response_model=RevisionQueueResponse)
async def revision_queue_today(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    svc = RevisionService(session)
    return await svc.get_today_queue(current_user.id, limit=limit, offset=offset)


@router.get("/stats", response_model=RevisionStatsResponse)
async def revision_stats(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    svc = RevisionService(session)
    return await svc.get_stats(current_user.id)


@router.get("/history", response_model=list[HistoryDay])
async def revision_history(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    svc = RevisionService(session)
    return await svc.get_history(current_user.id, days=days)


@router.get("/{question_id}", response_model=RevisionResponse)
async def get_revision_state(
    question_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    svc = RevisionService(session)
    out = await svc.get_revision(current_user.id, question_id)
    if not out:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Revision not found")
    return out


@router.delete("/{question_id}")
async def delete_revision(
    question_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    svc = RevisionService(session)
    ok = await svc.remove_from_revision(current_user.id, question_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Revision not found")
    return {"ok": True}


@router.post("/{question_id}/answer", response_model=RevisionResponse)
async def answer_revision(
    question_id: str,
    body: RevisionAnswer,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    svc = RevisionService(session)
    try:
        return await svc.record_answer(current_user.id, question_id, body.quality)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
