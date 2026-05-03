"""Revision CRUD, queue, stats."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import func as sa_func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.questions.models import Question
from app.domains.revisions.models import UserQuestionRevision
from app.domains.revisions import sm2_engine
from app.domains.revisions.schemas import (
    HistoryDay,
    MasteryDistribution,
    RevisionQueueItem,
    RevisionQueueResponse,
    RevisionResponse,
    RevisionStatsResponse,
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _preview_text(text: str, max_len: int = 160) -> str:
    t = (text or "").strip().replace("\n", " ")
    if len(t) <= max_len:
        return t
    return t[: max_len - 1] + "…"


def _topic_tag_from_question(q: Question) -> Optional[str]:
    t0 = q.tier_0_classification or {}
    if isinstance(t0, dict):
        topic = t0.get("topic") or t0.get("primary_topic")
        if isinstance(topic, str) and topic.strip():
            return topic.strip()
    return None


class RevisionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_question_by_public_id(self, question_id_str: str) -> Optional[Question]:
        stmt = select(Question).where(Question.question_id == question_id_str)
        row = await self.session.execute(stmt)
        return row.scalar_one_or_none()

    def _to_response(
        self,
        rev: UserQuestionRevision,
        question_id_str: str,
        *,
        now: Optional[datetime] = None,
    ) -> RevisionResponse:
        now = now or _utc_now()
        nr = rev.next_revision_at
        if nr.tzinfo is None:
            nr = nr.replace(tzinfo=timezone.utc)
        overdue_sec = (now - nr).total_seconds()
        days_overdue = max(0.0, round(overdue_sec / 86400.0, 2)) if overdue_sec > 0 else 0.0

        return RevisionResponse(
            id=rev.id,
            user_id=rev.user_id,
            question_uuid=rev.question_uuid,
            question_id_str=question_id_str,
            last_attempted_at=rev.last_attempted_at,
            last_result=rev.last_result,
            revision_count=rev.revision_count,
            interval_days=rev.interval_days,
            next_revision_at=rev.next_revision_at,
            ease_factor=rev.ease_factor,
            difficulty=rev.difficulty,
            streak=rev.streak,
            created_at=rev.created_at,
            updated_at=rev.updated_at,
            days_overdue=days_overdue,
        )

    async def add_to_revision(
        self,
        user_id: int,
        question_id_str: str,
        difficulty: str = "medium",
    ) -> RevisionResponse:
        q = await self._get_question_by_public_id(question_id_str)
        if not q:
            raise ValueError("Question not found")

        stmt = select(UserQuestionRevision).where(
            UserQuestionRevision.user_id == user_id,
            UserQuestionRevision.question_uuid == q.id,
        )
        row = await self.session.execute(stmt)
        existing = row.scalar_one_or_none()
        if existing:
            existing.difficulty = difficulty
            self.session.add(existing)
            await self.session.flush()
            return self._to_response(existing, q.question_id)

        now = _utc_now()
        next_at = now + timedelta(days=1)
        rev = UserQuestionRevision(
            user_id=user_id,
            question_uuid=q.id,
            last_attempted_at=None,
            last_result=None,
            revision_count=0,
            interval_days=1.0,
            next_revision_at=next_at,
            ease_factor=2.5,
            difficulty=difficulty,
            streak=0,
        )
        self.session.add(rev)
        await self.session.flush()
        await self.session.refresh(rev)
        return self._to_response(rev, q.question_id)

    async def remove_from_revision(self, user_id: int, question_id_str: str) -> bool:
        q = await self._get_question_by_public_id(question_id_str)
        if not q:
            return False
        stmt = select(UserQuestionRevision).where(
            UserQuestionRevision.user_id == user_id,
            UserQuestionRevision.question_uuid == q.id,
        )
        row = await self.session.execute(stmt)
        rev = row.scalar_one_or_none()
        if not rev:
            return False
        self.session.delete(rev)
        return True

    async def get_revision(self, user_id: int, question_id_str: str) -> Optional[RevisionResponse]:
        q = await self._get_question_by_public_id(question_id_str)
        if not q:
            return None
        stmt = select(UserQuestionRevision).where(
            UserQuestionRevision.user_id == user_id,
            UserQuestionRevision.question_uuid == q.id,
        )
        row = await self.session.execute(stmt)
        rev = row.scalar_one_or_none()
        if not rev:
            return None
        return self._to_response(rev, q.question_id)

    async def get_today_queue(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> RevisionQueueResponse:
        now = _utc_now()

        count_stmt = (
            select(sa_func.count())
            .select_from(UserQuestionRevision)
            .where(UserQuestionRevision.user_id == user_id)
            .where(UserQuestionRevision.next_revision_at <= now)
        )
        total = int((await self.session.execute(count_stmt)).scalar_one() or 0)

        overdue_epoch = sa_func.extract(
            "epoch",
            sa_func.now() - UserQuestionRevision.next_revision_at,
        )

        stmt = (
            select(UserQuestionRevision, Question)
            .join(Question, UserQuestionRevision.question_uuid == Question.id)
            .where(UserQuestionRevision.user_id == user_id)
            .where(UserQuestionRevision.next_revision_at <= now)
            .order_by(
                desc(overdue_epoch),
                UserQuestionRevision.ease_factor.asc(),
                UserQuestionRevision.revision_count.asc(),
            )
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        items: list[RevisionQueueItem] = []
        for rev, question in result.all():
            items.append(
                RevisionQueueItem(
                    revision=self._to_response(rev, question.question_id, now=now),
                    question_text_preview=_preview_text(
                        question.question_text_latex or question.question_text or ""
                    ),
                    subject=question.subject or "",
                    year=question.year,
                    question_number=question.question_number,
                    topic_tag=_topic_tag_from_question(question),
                )
            )

        return RevisionQueueResponse(total_due=total, items=items)

    async def record_answer(
        self,
        user_id: int,
        question_id_str: str,
        quality: str,
    ) -> RevisionResponse:
        q = await self._get_question_by_public_id(question_id_str)
        if not q:
            raise ValueError("Question not found")

        stmt = select(UserQuestionRevision).where(
            UserQuestionRevision.user_id == user_id,
            UserQuestionRevision.question_uuid == q.id,
        )
        row = await self.session.execute(stmt)
        rev = row.scalar_one_or_none()
        if not rev:
            raise ValueError("Revision not tracked for this question")

        qval = sm2_engine.quality_to_int(quality)
        now = _utc_now()
        out = sm2_engine.calculate_next_revision(
            qval,
            rev.interval_days,
            rev.ease_factor,
            rev.revision_count,
            rev.streak,
            rev.difficulty,
            now=now,
        )

        rev.last_attempted_at = now
        rev.last_result = quality
        rev.revision_count = rev.revision_count + 1
        rev.interval_days = out.new_interval
        rev.next_revision_at = out.next_revision_at
        rev.ease_factor = out.new_ease_factor
        rev.streak = out.new_streak
        self.session.add(rev)
        await self.session.flush()
        await self.session.refresh(rev)
        return self._to_response(rev, q.question_id)

    async def _distinct_attempt_dates(self, user_id: int) -> set[date]:
        stmt = select(UserQuestionRevision.last_attempted_at).where(
            UserQuestionRevision.user_id == user_id,
            UserQuestionRevision.last_attempted_at.isnot(None),
        )
        rows = (await self.session.execute(stmt)).scalars().all()
        out: set[date] = set()
        for dt in rows:
            if dt is None:
                continue
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            out.add(dt.astimezone(timezone.utc).date())
        return out

    @staticmethod
    def _streak_from_dates(dates: set[date]) -> int:
        today = _utc_now().date()
        streak = 0
        d = today
        if d not in dates:
            d = today - timedelta(days=1)
        while d in dates:
            streak += 1
            d -= timedelta(days=1)
        return streak

    async def get_stats(self, user_id: int) -> RevisionStatsResponse:
        now = _utc_now()
        week_end = now + timedelta(days=7)

        base = select(UserQuestionRevision).where(UserQuestionRevision.user_id == user_id)

        due_today_stmt = select(sa_func.count()).select_from(UserQuestionRevision).where(
            UserQuestionRevision.user_id == user_id,
            UserQuestionRevision.next_revision_at <= now,
        )
        due_week_stmt = select(sa_func.count()).select_from(UserQuestionRevision).where(
            UserQuestionRevision.user_id == user_id,
            UserQuestionRevision.next_revision_at <= week_end,
        )
        total_stmt = select(sa_func.count()).select_from(UserQuestionRevision).where(
            UserQuestionRevision.user_id == user_id,
        )

        due_today = int((await self.session.execute(due_today_stmt)).scalar_one() or 0)
        due_week = int((await self.session.execute(due_week_stmt)).scalar_one() or 0)
        total_tracked = int((await self.session.execute(total_stmt)).scalar_one() or 0)

        new_stmt = select(sa_func.count()).select_from(UserQuestionRevision).where(
            UserQuestionRevision.user_id == user_id,
            UserQuestionRevision.revision_count == 0,
        )
        learning_stmt = select(sa_func.count()).select_from(UserQuestionRevision).where(
            UserQuestionRevision.user_id == user_id,
            UserQuestionRevision.revision_count >= 1,
            UserQuestionRevision.revision_count <= 5,
        )
        mature_stmt = select(sa_func.count()).select_from(UserQuestionRevision).where(
            UserQuestionRevision.user_id == user_id,
            UserQuestionRevision.revision_count >= 6,
        )

        new_c = int((await self.session.execute(new_stmt)).scalar_one() or 0)
        learning_c = int((await self.session.execute(learning_stmt)).scalar_one() or 0)
        mature_c = int((await self.session.execute(mature_stmt)).scalar_one() or 0)

        dates = await self._distinct_attempt_dates(user_id)
        streak_n = self._streak_from_dates(dates)

        return RevisionStatsResponse(
            due_today=due_today,
            due_this_week=due_week,
            total_tracked=total_tracked,
            current_streak=streak_n,
            mastery=MasteryDistribution(new=new_c, learning=learning_c, mature=mature_c),
        )

    async def get_history(self, user_id: int, days: int = 30) -> list[HistoryDay]:
        days = max(1, min(days, 365))
        end = _utc_now().date()
        start = end - timedelta(days=days - 1)

        stmt = select(UserQuestionRevision.last_attempted_at).where(
            UserQuestionRevision.user_id == user_id,
            UserQuestionRevision.last_attempted_at.isnot(None),
        )
        rows = (await self.session.execute(stmt)).scalars().all()

        counts: dict[date, int] = {}
        for dt in rows:
            if dt is None:
                continue
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            d = dt.astimezone(timezone.utc).date()
            if d < start or d > end:
                continue
            counts[d] = counts.get(d, 0) + 1

        out: list[HistoryDay] = []
        cur = start
        while cur <= end:
            out.append(HistoryDay(date=cur.isoformat(), count=counts.get(cur, 0)))
            cur += timedelta(days=1)
        return out
