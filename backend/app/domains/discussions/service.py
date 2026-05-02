from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
import uuid

from app.domains.auth.models import User
from app.domains.discussions.models import Discussion
from app.domains.discussions.schemas import DiscussionCreate, DiscussionResponse


class DiscussionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_response(
        discussion: Discussion,
        full_name: Optional[str],
        email: Optional[str],
    ) -> DiscussionResponse:
        return DiscussionResponse(
            id=discussion.id,
            question_id=discussion.question_id,
            user_id=discussion.user_id,
            content=discussion.content,
            parent_id=discussion.parent_id,
            upvotes=discussion.upvotes,
            downvotes=discussion.downvotes,
            created_at=discussion.created_at,
            updated_at=discussion.updated_at,
            user_name=full_name if full_name else None,
            user_email=email if email else None,
        )

    async def _response_with_user(self, discussion: Discussion) -> DiscussionResponse:
        stmt_u = select(User.full_name, User.email).where(User.id == discussion.user_id)
        row = (await self.session.execute(stmt_u)).first()
        fn, em = (row[0], row[1]) if row else (None, None)
        return self._to_response(discussion, fn, em)

    async def get_discussions(self, question_id: uuid.UUID) -> List[DiscussionResponse]:
        """
        Discussions for a question, newest first, with commenter name/email from users table.
        """
        stmt = (
            select(Discussion, User.full_name, User.email)
            .outerjoin(User, Discussion.user_id == User.id)
            .where(Discussion.question_id == question_id)
            .order_by(desc(Discussion.created_at))
        )
        result = await self.session.execute(stmt)
        rows = result.all()
        return [self._to_response(d, fn, em) for d, fn, em in rows]

    async def create_discussion(
        self,
        question_id: uuid.UUID,
        user_id: int,
        discussion_in: DiscussionCreate,
    ) -> DiscussionResponse:
        discussion = Discussion(
            question_id=question_id,
            user_id=user_id,
            content=discussion_in.content,
            parent_id=discussion_in.parent_id,
        )
        self.session.add(discussion)
        await self.session.commit()
        await self.session.refresh(discussion)
        return await self._response_with_user(discussion)

    async def vote_discussion(
        self,
        discussion_id: uuid.UUID,
        vote_type: str,
        _user_id: int,
    ) -> Optional[DiscussionResponse]:
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
        return await self._response_with_user(discussion)

    async def delete_discussion(self, discussion_id: uuid.UUID, user_id: int) -> bool:
        stmt = select(Discussion).where(Discussion.id == discussion_id)
        result = await self.session.execute(stmt)
        discussion = result.scalar_one_or_none()

        if not discussion:
            return False

        if discussion.user_id != user_id:
            return False

        await self.session.delete(discussion)
        await self.session.commit()
        return True
