from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid

class Discussion(SQLModel, table=True):
    __tablename__ = "discussions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    question_id: uuid.UUID = Field(index=True, nullable=False)
    user_id: int = Field(index=True, nullable=False)
    content: str = Field(nullable=False)
    parent_id: Optional[uuid.UUID] = Field(default=None, index=True)
    upvotes: int = Field(default=0)
    downvotes: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
