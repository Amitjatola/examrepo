"""Bookmarks + notes per user/question."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.domains.auth.deps import get_current_user
from app.domains.auth.models import User
from app.domains.questions.models import Question, UserQuestionBookmark
from app.domains.questions.schemas import BookmarkRead, BookmarkUpsert

router = APIRouter(prefix="/users/me", tags=["bookmarks"])


@router.get("/bookmarks", response_model=list[BookmarkRead])
async def list_bookmarks(
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(UserQuestionBookmark, Question.question_id)
        .join(Question, UserQuestionBookmark.question_uuid == Question.id)
        .where(UserQuestionBookmark.user_id == current_user.id)
        .where(UserQuestionBookmark.is_bookmarked.is_(True))
        .order_by(UserQuestionBookmark.updated_at.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    out: list[BookmarkRead] = []
    for row, qid in result.all():
        out.append(
            BookmarkRead(
                question_id=qid,
                note=row.note,
                is_bookmarked=row.is_bookmarked,
                updated_at=row.updated_at,
            )
        )
    return out


@router.get("/bookmarks/{question_id}", response_model=BookmarkRead)
async def get_bookmark(
    question_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    q_stmt = select(Question).where(Question.question_id == question_id)
    q_row = await session.execute(q_stmt)
    question = q_row.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    b_stmt = select(UserQuestionBookmark).where(
        UserQuestionBookmark.user_id == current_user.id,
        UserQuestionBookmark.question_uuid == question.id,
    )
    b_row = await session.execute(b_stmt)
    bm = b_row.scalar_one_or_none()
    if not bm:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    return BookmarkRead(
        question_id=question.question_id,
        note=bm.note,
        is_bookmarked=bm.is_bookmarked,
        updated_at=bm.updated_at,
    )


@router.put("/bookmarks/{question_id}", response_model=BookmarkRead)
async def upsert_bookmark(
    question_id: str,
    body: BookmarkUpsert,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    q_stmt = select(Question).where(Question.question_id == question_id)
    q_row = await session.execute(q_stmt)
    question = q_row.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    b_stmt = select(UserQuestionBookmark).where(
        UserQuestionBookmark.user_id == current_user.id,
        UserQuestionBookmark.question_uuid == question.id,
    )
    b_row = await session.execute(b_stmt)
    bm = b_row.scalar_one_or_none()
    now = datetime.utcnow()

    if bm:
        bm.note = body.note
        bm.is_bookmarked = body.is_bookmarked
        bm.updated_at = now
        session.add(bm)
    else:
        bm = UserQuestionBookmark(
            user_id=current_user.id,
            question_uuid=question.id,
            note=body.note,
            is_bookmarked=body.is_bookmarked,
            updated_at=now,
        )
        session.add(bm)

    await session.commit()
    await session.refresh(bm)

    return BookmarkRead(
        question_id=question.question_id,
        note=bm.note,
        is_bookmarked=bm.is_bookmarked,
        updated_at=bm.updated_at,
    )


@router.delete("/bookmarks/{question_id}")
async def delete_bookmark(
    question_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    q_stmt = select(Question).where(Question.question_id == question_id)
    q_row = await session.execute(q_stmt)
    question = q_row.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    b_stmt = select(UserQuestionBookmark).where(
        UserQuestionBookmark.user_id == current_user.id,
        UserQuestionBookmark.question_uuid == question.id,
    )
    b_row = await session.execute(b_stmt)
    bm = b_row.scalar_one_or_none()
    if not bm:
        return {"status": "ok", "deleted": False}

    session.delete(bm)
    await session.commit()
    return {"status": "ok", "deleted": True}
