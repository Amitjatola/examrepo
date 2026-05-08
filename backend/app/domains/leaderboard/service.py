"""Leaderboard aggregation and privacy-safe display names."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.auth.models import User, generate_leaderboard_alias
from app.domains.leaderboard.schemas import (
    LeaderboardEntry,
    LeaderboardResponse,
    LeaderboardUserInfo,
)
from app.domains.questions.models import UserAttempt
from app.domains.revisions.models import UserQuestionRevision


def _composite_score(accuracy_pct: float, questions_solved: int, revision_streak: int) -> float:
    volume_part = min(max(questions_solved, 0), 500) / 500 * 30
    streak_part = min(max(revision_streak, 0), 30) / 30 * 30
    acc_part = max(0.0, min(100.0, accuracy_pct)) * 0.4
    return round(acc_part + volume_part + streak_part, 2)


def _display_name(u: User) -> str:
    if (u.leaderboard_visibility or "anonymous").lower() == "public":
        name = (u.full_name or "").strip()
        return name if name else "Learner"
    alias = (u.leaderboard_alias or "").strip()
    if alias:
        return alias
    if u.id is not None:
        return generate_leaderboard_alias(u.id)
    return "Learner"


@dataclass
class _Row:
    user_id: int
    questions_solved: int
    total_attempts: int
    correct_attempts: int
    revision_streak: int


class LeaderboardService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_leaderboard_info(self, user_id: int) -> Optional[LeaderboardUserInfo]:
        stmt = select(User).where(User.id == user_id)
        u = (await self.session.execute(stmt)).scalar_one_or_none()
        if not u:
            return None
        alias = (u.leaderboard_alias or "").strip()
        if not alias and u.id is not None:
            alias = generate_leaderboard_alias(u.id)
        return LeaderboardUserInfo(visibility=u.leaderboard_visibility or "anonymous", alias=alias)

    async def update_visibility(self, user_id: int, visibility: str) -> Optional[LeaderboardUserInfo]:
        stmt = select(User).where(User.id == user_id)
        u = (await self.session.execute(stmt)).scalar_one_or_none()
        if not u:
            return None
        u.leaderboard_visibility = visibility
        self.session.add(u)
        await self.session.flush()
        return await self.get_user_leaderboard_info(user_id)

    async def _fetch_aggregate_rows(self) -> list[_Row]:
        distinct_correct_q = func.count(
            func.distinct(case((UserAttempt.is_correct.is_(True), UserAttempt.question_id), else_=None))
        )
        att_sub = (
            select(
                UserAttempt.user_id.label("uid"),
                func.count().label("total_attempts"),
                func.sum(case((UserAttempt.is_correct.is_(True), 1), else_=0)).label("correct_attempts"),
                distinct_correct_q.label("questions_solved"),
            )
            .group_by(UserAttempt.user_id)
            .subquery()
        )

        rev_sub = (
            select(
                UserQuestionRevision.user_id.label("uid"),
                func.max(UserQuestionRevision.streak).label("max_streak"),
            )
            .group_by(UserQuestionRevision.user_id)
            .subquery()
        )

        stmt = (
            select(
                att_sub.c.uid,
                att_sub.c.questions_solved,
                att_sub.c.total_attempts,
                att_sub.c.correct_attempts,
                func.coalesce(rev_sub.c.max_streak, 0).label("revision_streak"),
            )
            .select_from(att_sub.outerjoin(rev_sub, att_sub.c.uid == rev_sub.c.uid))
            .where(att_sub.c.total_attempts >= 1)
        )

        result = await self.session.execute(stmt)
        rows = []
        for r in result.all():
            rows.append(
                _Row(
                    user_id=int(r.uid),
                    questions_solved=int(r.questions_solved or 0),
                    total_attempts=int(r.total_attempts or 0),
                    correct_attempts=int(r.correct_attempts or 0),
                    revision_streak=int(r.revision_streak or 0),
                )
            )
        return rows

    async def get_leaderboard(
        self,
        current_user_id: int,
        *,
        sort_by: str = "composite",
        limit: int = 50,
        offset: int = 0,
    ) -> LeaderboardResponse:
        agg = await self._fetch_aggregate_rows()
        if not agg:
            return LeaderboardResponse(
                entries=[],
                current_user_rank=None,
                current_user_percentile=None,
                total_participants=0,
            )

        user_ids = [r.user_id for r in agg]
        u_stmt = select(User).where(User.id.in_(user_ids))
        users = (await self.session.execute(u_stmt)).scalars().all()
        user_map = {u.id: u for u in users if u.id is not None}

        enriched: list[tuple[_Row, float, float]] = []
        for row in agg:
            total = row.total_attempts
            correct = row.correct_attempts
            accuracy_pct = round((correct / total) * 100, 2) if total else 0.0
            comp = _composite_score(accuracy_pct, row.questions_solved, row.revision_streak)
            enriched.append((row, accuracy_pct, comp))

        if sort_by == "accuracy":
            enriched.sort(key=lambda x: (x[1], x[2], x[0].questions_solved, x[0].user_id), reverse=True)
        elif sort_by == "questions_solved":
            enriched.sort(
                key=lambda x: (x[0].questions_solved, x[2], x[1], x[0].user_id),
                reverse=True,
            )
        else:
            enriched.sort(key=lambda x: (x[2], x[1], x[0].questions_solved, x[0].user_id), reverse=True)

        total_participants = len(enriched)
        rank_by_user: dict[int, int] = {}
        for idx, (row, _, comp) in enumerate(enriched, start=1):
            rank_by_user[row.user_id] = idx

        current_rank = rank_by_user.get(current_user_id)
        current_pct: Optional[float] = None
        if current_rank is not None and total_participants > 0:
            current_pct = round(100.0 * current_rank / total_participants, 1)

        page = enriched[offset : offset + limit]
        entries: list[LeaderboardEntry] = []
        for row, accuracy_pct, comp in page:
            rank = rank_by_user[row.user_id]
            u = user_map.get(row.user_id)
            display = _display_name(u) if u else "Learner"
            entries.append(
                LeaderboardEntry(
                    rank=rank,
                    display_name=display,
                    is_current_user=row.user_id == current_user_id,
                    questions_solved=row.questions_solved,
                    accuracy_pct=accuracy_pct,
                    revision_streak=row.revision_streak,
                    composite_score=comp,
                )
            )

        return LeaderboardResponse(
            entries=entries,
            current_user_rank=current_rank,
            current_user_percentile=current_pct,
            total_participants=total_participants,
        )
