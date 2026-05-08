"""Mistake Museum API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.domains.auth.deps import get_current_user
from app.domains.auth.models import User
from app.domains.mistakes.schemas import (
    MistakeAnnotationUpdate,
    MistakeMuseumItem,
    MistakeMuseumResponse,
    MistakeSummary,
    RepeatOffenderItem,
)
from app.domains.mistakes.service import MistakeService
from app.domains.revisions.service import RevisionService

router = APIRouter(prefix="/mistakes", tags=["mistakes"])


@router.get("", response_model=MistakeMuseumResponse)
async def list_mistakes(
    topic: Optional[str] = Query(None),
    error_type: Optional[str] = Query(None),
    only_unresolved: bool = Query(False),
    sort_by: str = Query("repeat_count"),
    limit: int = Query(30, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    svc = MistakeService(session)
    return await svc.get_museum(
        current_user.id,
        topic=topic,
        error_type=error_type,
        only_unresolved=only_unresolved,
        sort_by=sort_by,
        limit=limit,
        offset=offset,
    )


@router.get("/summary", response_model=MistakeSummary)
async def mistake_summary(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    svc = MistakeService(session)
    return await svc.get_summary(current_user.id)


@router.get("/repeat-offenders", response_model=list[RepeatOffenderItem])
async def repeat_offenders(
    min_wrong: int = Query(3, ge=2, le=20),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    svc = MistakeService(session)
    return await svc.get_repeat_offenders(current_user.id, min_wrong=min_wrong, limit=limit)


@router.patch("/{question_id}", response_model=MistakeMuseumItem)
async def update_mistake(
    question_id: str,
    body: MistakeAnnotationUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    svc = MistakeService(session)
    kwargs = {}
    if body.error_type is not None:
        kwargs["error_type"] = body.error_type
    if body.is_resolved is not None:
        kwargs["is_resolved"] = body.is_resolved
    if body.notes is not None:
        kwargs["notes"] = body.notes
    if not kwargs:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nothing to update")
    out = await svc.update_annotation(current_user.id, question_id, **kwargs)
    if not out:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mistake not found")
    return out


@router.post("/{question_id}/add-to-revision")
async def add_mistake_to_revision(
    question_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    rev_svc = RevisionService(session)
    try:
        out = await rev_svc.add_to_revision(current_user.id, question_id, "hard")
        return {"ok": True, "revision": out}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
