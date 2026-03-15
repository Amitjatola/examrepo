from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from app.core.database import get_session
from app.domains.auth.deps import get_current_user
from app.domains.auth.models import User
from app.domains.discussions.service import DiscussionService
from app.domains.discussions.schemas import DiscussionResponse, DiscussionCreate, VoteRequest

router = APIRouter()

@router.get("/questions/{question_id}/discussions", response_model=List[DiscussionResponse])
async def get_discussions(
    question_id: uuid.UUID,
    session: AsyncSession = Depends(get_session)
):
    service = DiscussionService(session)
    return await service.get_discussions(question_id)

@router.post("/questions/{question_id}/discussions", response_model=DiscussionResponse)
async def create_discussion(
    question_id: uuid.UUID,
    discussion_in: DiscussionCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    service = DiscussionService(session)
    return await service.create_discussion(question_id, current_user.id, discussion_in)

@router.post("/discussions/{discussion_id}/vote", response_model=DiscussionResponse)
async def vote_discussion(
    discussion_id: uuid.UUID,
    vote_in: VoteRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    service = DiscussionService(session)
    discussion = await service.vote_discussion(discussion_id, vote_in.vote_type, current_user.id)
    if not discussion:
        raise HTTPException(status_code=404, detail="Discussion not found")
    return discussion

@router.delete("/discussions/{discussion_id}")
async def delete_discussion(
    discussion_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    service = DiscussionService(session)
    success = await service.delete_discussion(discussion_id, current_user.id)
    if not success:
        raise HTTPException(status_code=403, detail="Not authorized or not found")
    return {"message": "Deleted successfully"}
