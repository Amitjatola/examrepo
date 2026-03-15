from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, update, delete
from typing import List, Optional
import uuid

from app.domains.discussions.models import Discussion
from app.domains.discussions.schemas import DiscussionCreate

class DiscussionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_discussions(self, question_id: uuid.UUID) -> List[Discussion]:
        """
        Get all discussions for a question.
        Frontend will handle threading/nesting.
        Sorted by created_at desc for now.
        """
        stmt = (
            select(Discussion)
            .where(Discussion.question_id == question_id)
            .order_by(desc(Discussion.created_at))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_discussion(self, question_id: uuid.UUID, user_id: int, discussion_in: DiscussionCreate) -> Discussion:
        discussion = Discussion(
            question_id=question_id,
            user_id=user_id,
            content=discussion_in.content,
            parent_id=discussion_in.parent_id
        )
        self.session.add(discussion)
        await self.session.commit()
        await self.session.refresh(discussion)
        return discussion

    async def vote_discussion(self, discussion_id: uuid.UUID, vote_type: str, user_id: int) -> Discussion:
        # MVP: Simple increment/decrement
        # Ideally: Check if user already voted in a separate table
        
        stmt = select(Discussion).where(Discussion.id == discussion_id)
        result = await self.session.execute(stmt)
        discussion = result.scalar_one_or_none()
        
        if not discussion:
            return None
            
        if vote_type == "upvote":
            discussion.upvotes += 1
        elif vote_type == "downvote":
            discussion.downvotes += 1
            
        self.session.add(discussion)
        await self.session.commit()
        await self.session.refresh(discussion)
        return discussion

    async def delete_discussion(self, discussion_id: uuid.UUID, user_id: int) -> bool:
        stmt = select(Discussion).where(Discussion.id == discussion_id)
        result = await self.session.execute(stmt)
        discussion = result.scalar_one_or_none()
        
        if not discussion:
            return False
            
        if discussion.user_id != user_id:
            # Unauthorized
            return False
            
        await self.session.delete(discussion)
        await self.session.commit()
        return True
