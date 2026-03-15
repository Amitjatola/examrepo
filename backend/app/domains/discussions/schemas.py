from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

class DiscussionBase(BaseModel):
    content: str
    parent_id: Optional[uuid.UUID] = None

class DiscussionCreate(DiscussionBase):
    pass

class DiscussionUpdate(BaseModel):
    content: Optional[str] = None

class DiscussionResponse(DiscussionBase):
    id: uuid.UUID
    question_id: uuid.UUID
    user_id: int
    upvotes: int
    downvotes: int
    created_at: datetime
    updated_at: datetime
    # We will handle nested replies in the frontend or service layer if needed
    # user details will be fetched separately or joined

    class Config:
        from_attributes = True

class VoteRequest(BaseModel):
    vote_type: str  # "upvote" or "downvote"
