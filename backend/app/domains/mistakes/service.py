"""Mistake Museum service — query, annotate, summarize."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func as sa_func, select, case, literal_column
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.mistakes.models import UserMistakeAnnotation
from app.domains.mistakes.schemas import (
    MistakeMuseumItem,
    MistakeMuseumResponse,
    MistakeSummary,
    RepeatOffenderItem,
)
from app.domains.questions.models import Question
from app.domains.revisions.models import UserQuestionRevision


def _preview(text: str, n: int = 140) -> str:
    t = (text or "").strip().replace("\n", " ")
    return t if len(t) <= n else t[: n - 1] + "…"


def _topic_tag(q: Question) -> Optional[str]:
    t0 = q.tier_0_classification or {}
    if isinstance(t0, dict):
        t = t0.get("topic") or t0.get("primary_topic")
        if isinstance(t, str) and t.strip():
            return t.strip()
    return None


class MistakeService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _resolve_question(self, question_id_str: str) -> Optional[Question]:
        stmt = select(Question).where(Question.question_id == question_id_str)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_museum(
        self,
        user_id: int,
        *,
        topic: Optional[str] = None,
        error_type: Optional[str] = None,
        only_unresolved: bool = False,
        sort_by: str = "repeat_count",
        limit: int = 30,
        offset: int = 0,
    ) -> MistakeMuseumResponse:
        base = (
            select(UserMistakeAnnotation, Question)
            .join(Question, UserMistakeAnnotation.question_uuid == Question.id)
            .where(UserMistakeAnnotation.user_id == user_id)
            .where(UserMistakeAnnotation.wrong_count > 0)
        )

        if topic:
            base = base.where(
                Question.tier_0_classification["topic"].as_string() == topic
            )
        if error_type:
            base = base.where(UserMistakeAnnotation.error_type == error_type)
        if only_unresolved:
            base = base.where(UserMistakeAnnotation.is_resolved.is_(False))

        count_stmt = select(sa_func.count()).select_from(
            base.with_only_columns(UserMistakeAnnotation.id).subquery()
        )
        total = int((await self.session.execute(count_stmt)).scalar_one() or 0)

        if sort_by == "recency":
            base = base.order_by(UserMistakeAnnotation.last_wrong_at.desc().nullslast())
        elif sort_by == "topic":
            base = base.order_by(Question.subject, Question.year)
        else:
            base = base.order_by(UserMistakeAnnotation.wrong_count.desc())

        base = base.limit(limit).offset(offset)
        rows = (await self.session.execute(base)).all()

        rev_uuids: set = set()
        if rows:
            quuids = [r[0].question_uuid for r in rows]
            rev_stmt = select(UserQuestionRevision.question_uuid).where(
                UserQuestionRevision.user_id == user_id,
                UserQuestionRevision.question_uuid.in_(quuids),
            )
            rev_uuids = set((await self.session.execute(rev_stmt)).scalars().all())

        items: list[MistakeMuseumItem] = []
        for ann, q in rows:
            total_attempts = ann.wrong_count + ann.correct_count
            imp = round(ann.correct_count / total_attempts * 100, 1) if total_attempts else 0.0
            items.append(
                MistakeMuseumItem(
                    question_id_str=q.question_id,
                    subject=q.subject or "",
                    year=q.year,
                    question_number=q.question_number,
                    topic_tag=_topic_tag(q),
                    question_text_preview=_preview(q.question_text_latex or q.question_text or ""),
                    wrong_count=ann.wrong_count,
                    correct_count=ann.correct_count,
                    error_type=ann.error_type,
                    is_resolved=ann.is_resolved,
                    last_wrong_at=ann.last_wrong_at,
                    last_correct_at=ann.last_correct_at,
                    notes=ann.notes,
                    improvement_pct=imp,
                    in_revision=ann.question_uuid in rev_uuids,
                )
            )

        summary = await self.get_summary(user_id)
        return MistakeMuseumResponse(total=total, items=items, summary=summary)

    async def get_summary(self, user_id: int) -> MistakeSummary:
        base = select(UserMistakeAnnotation).where(
            UserMistakeAnnotation.user_id == user_id,
            UserMistakeAnnotation.wrong_count > 0,
        )

        total = int(
            (await self.session.execute(
                select(sa_func.count()).select_from(base.subquery())
            )).scalar_one() or 0
        )
        resolved = int(
            (await self.session.execute(
                select(sa_func.count()).select_from(
                    base.where(UserMistakeAnnotation.is_resolved.is_(True)).subquery()
                )
            )).scalar_one() or 0
        )

        type_stmt = (
            select(
                UserMistakeAnnotation.error_type,
                sa_func.count().label("cnt"),
            )
            .where(UserMistakeAnnotation.user_id == user_id, UserMistakeAnnotation.wrong_count > 0)
            .group_by(UserMistakeAnnotation.error_type)
        )
        type_rows = (await self.session.execute(type_stmt)).all()
        type_map = {r[0]: r[1] for r in type_rows}

        topic_stmt = (
            select(
                Question.tier_0_classification["topic"].as_string().label("topic"),
                sa_func.sum(UserMistakeAnnotation.wrong_count).label("wc"),
            )
            .join(Question, UserMistakeAnnotation.question_uuid == Question.id)
            .where(UserMistakeAnnotation.user_id == user_id, UserMistakeAnnotation.wrong_count > 0)
            .group_by(literal_column("topic"))
            .order_by(sa_func.sum(UserMistakeAnnotation.wrong_count).desc())
            .limit(5)
        )
        topic_rows = (await self.session.execute(topic_stmt)).all()
        top_weak = [{"topic": r[0] or "Unknown", "wrong_count": int(r[1])} for r in topic_rows if r[0]]

        return MistakeSummary(
            total_mistakes=total,
            resolved_count=resolved,
            conceptual_count=type_map.get("conceptual", 0),
            careless_count=type_map.get("careless", 0),
            tricky_count=type_map.get("tricky", 0),
            untagged_count=type_map.get(None, 0),
            top_weak_topics=top_weak,
        )

    async def update_annotation(
        self,
        user_id: int,
        question_id_str: str,
        *,
        error_type: Optional[str] = ...,
        is_resolved: Optional[bool] = ...,
        notes: Optional[str] = ...,
    ) -> Optional[MistakeMuseumItem]:
        q = await self._resolve_question(question_id_str)
        if not q:
            return None
        stmt = select(UserMistakeAnnotation).where(
            UserMistakeAnnotation.user_id == user_id,
            UserMistakeAnnotation.question_uuid == q.id,
        )
        ann = (await self.session.execute(stmt)).scalar_one_or_none()
        if not ann:
            return None

        if error_type is not ...:
            ann.error_type = error_type
        if is_resolved is not ...:
            ann.is_resolved = is_resolved if is_resolved is not None else ann.is_resolved
        if notes is not ...:
            ann.notes = notes

        self.session.add(ann)
        await self.session.flush()

        total_attempts = ann.wrong_count + ann.correct_count
        imp = round(ann.correct_count / total_attempts * 100, 1) if total_attempts else 0.0

        rev_stmt = select(UserQuestionRevision.id).where(
            UserQuestionRevision.user_id == user_id,
            UserQuestionRevision.question_uuid == q.id,
        )
        in_rev = (await self.session.execute(rev_stmt)).scalar_one_or_none() is not None

        return MistakeMuseumItem(
            question_id_str=q.question_id,
            subject=q.subject or "",
            year=q.year,
            question_number=q.question_number,
            topic_tag=_topic_tag(q),
            question_text_preview=_preview(q.question_text_latex or q.question_text or ""),
            wrong_count=ann.wrong_count,
            correct_count=ann.correct_count,
            error_type=ann.error_type,
            is_resolved=ann.is_resolved,
            last_wrong_at=ann.last_wrong_at,
            last_correct_at=ann.last_correct_at,
            notes=ann.notes,
            improvement_pct=imp,
            in_revision=in_rev,
        )

    async def get_repeat_offenders(
        self,
        user_id: int,
        min_wrong: int = 3,
        limit: int = 20,
    ) -> list[RepeatOffenderItem]:
        rev_sub = (
            select(UserQuestionRevision.question_uuid)
            .where(UserQuestionRevision.user_id == user_id)
            .subquery()
        )
        stmt = (
            select(UserMistakeAnnotation, Question)
            .join(Question, UserMistakeAnnotation.question_uuid == Question.id)
            .where(
                UserMistakeAnnotation.user_id == user_id,
                UserMistakeAnnotation.wrong_count >= min_wrong,
                UserMistakeAnnotation.is_resolved.is_(False),
                UserMistakeAnnotation.question_uuid.notin_(select(rev_sub)),
            )
            .order_by(UserMistakeAnnotation.wrong_count.desc())
            .limit(limit)
        )
        rows = (await self.session.execute(stmt)).all()
        return [
            RepeatOffenderItem(
                question_id_str=q.question_id,
                wrong_count=ann.wrong_count,
                subject=q.subject or "",
                topic_tag=_topic_tag(q),
            )
            for ann, q in rows
        ]
