"""
Question service for business logic.
Orchestrates between API and repository layers.
"""

from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Optional
import uuid
import random

from app.domains.questions.repository import QuestionRepository
from app.domains.questions.schemas import (
    QuestionCreate,
    QuestionResponse,
    QuestionListItem,
    SearchFilters,
    SearchResult,
    FilterOptions,
    DashboardStats,
    MockPaperRequest,
    GapDrillResponse,
)
from app.domains.questions.models import Question, UserAttempt
from app.domains.questions.readiness_lite import compute_readiness_lite


class QuestionService:
    """Service layer for question business logic."""
    
    def __init__(self, session: AsyncSession):
        self.repo = QuestionRepository(session)
    
    async def get_question(self, question_id: uuid.UUID) -> Optional[QuestionResponse]:
        """Get a single question by ID."""
        question = await self.repo.get_by_id(question_id)
        if not question:
            return None
        return QuestionResponse.model_validate(question)
    
    async def get_question_by_string_id(self, question_id: str) -> Optional[QuestionResponse]:
        """Get a single question by string ID (e.g., GATE_AE_2008_Q01)."""
        question = await self.repo.get_by_question_id(question_id)
        if not question:
            return None
        return QuestionResponse.model_validate(question)
    
    async def search_questions(
        self,
        query: str,
        filters: Optional[SearchFilters] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> SearchResult:
        """Search questions with filters and pagination."""
        questions, total = await self.repo.search(query, filters, page, page_size)
        
        # Convert to list items with extracted metadata
        items = []
        for q in questions:
            item = self._to_list_item(q)
            items.append(item)
        
        return SearchResult(
            query=query,
            total=total,
            page=page,
            page_size=page_size,
            filters_applied=filters.model_dump(exclude_none=True) if filters else {},
            questions=items,
        )
    
    def _to_list_item(self, question: Question) -> QuestionListItem:
        """Convert Question model to lightweight list item."""
        # Extract difficulty from tier_0
        # Extract difficulty from tier_0
        difficulty_score = None
        difficulty_level = "Medium"
        if question.tier_0_classification:
            difficulty_score = question.tier_0_classification.get("difficulty_score")
            if difficulty_score is not None:
                if difficulty_score <= 4:
                    difficulty_level = "Easy"
                elif difficulty_score >= 8:
                    difficulty_level = "Hard"
                else:
                    difficulty_level = "Medium"
        
        # Extract topic and concepts from tier_1
        topic = None
        concepts = []
        if question.tier_1_core_research:
            tags = question.tier_1_core_research.get("hierarchical_tags", {})
            if tags.get("topic"):
                topic = tags["topic"].get("name")
            if tags.get("concepts"):
                concepts = [c.get("name", "") for c in tags["concepts"] if c.get("name")]
        
        # Extract explanation from tier_1
        explanation = None
        if question.tier_1_core_research:
            explanation = question.tier_1_core_research.get("explanation")
        
        return QuestionListItem(
            id=question.id,
            question_id=question.question_id,
            year=question.year,
            question_number=question.question_number,
            subject=question.subject,
            question_text=question.question_text[:1000] if len(question.question_text) > 1000 else question.question_text,
            question_text_latex=question.question_text_latex,
            question_type=question.question_type,
            marks=question.marks,
            difficulty_score=difficulty_score,
            difficulty_level=difficulty_level,
            topic=topic,
            concepts=concepts[:5],  # Limit to 5 concepts
            options=question.options,
            answer_key=question.answer_key,
            explanation=explanation,
        )
    
    async def get_filter_options(self) -> FilterOptions:
        """Get available filter options."""
        options = await self.repo.get_filter_options()
        return FilterOptions(**options)
    
    async def import_question(self, data: dict) -> QuestionResponse:
        """Import a single question from JSON data."""
        question_data = QuestionCreate(**data)
        question = await self.repo.create(question_data)
        return QuestionResponse.model_validate(question)
    
    async def bulk_import(self, questions_data: list[dict]) -> dict:
        """Bulk import questions from JSON."""
        count = await self.repo.bulk_create(questions_data)
        total = await self.repo.count_all()
        return {
            "imported": count,
            "total_in_db": total,
        }

    async def get_syllabus_tree(self) -> dict:
        """Get the full syllabus tree."""
        return await self.repo.get_syllabus_tree()

    async def get_user_dashboard_stats(self, user_id: int, target_band: str = "good") -> DashboardStats:
        """Calculate dashboard statistics for a user."""
        # This belongs in a repo, but for now we put it here or access a new repo
        # To avoid circular imports or complexity, we'll do a direct query for now
        # Ideally we should have a UserAttemptRepository
        
        from sqlalchemy import select, func

        # Count total questions
        total_questions = await self.repo.count_all()
        
        # Count distinct questions attempted by user
        # We verify attempts against actual user_id
        statement = select(func.count(func.distinct(UserAttempt.question_id))).where(UserAttempt.user_id == user_id)
        result = await self.repo.session.execute(statement)
        attempted_count = result.scalar() or 0
        
        # Calculate total time taken
        time_stmt = select(func.sum(UserAttempt.time_taken_seconds)).where(UserAttempt.user_id == user_id)
        time_result = await self.repo.session.execute(time_stmt)
        total_seconds = time_result.scalar() or 0
        hours_studied = round(total_seconds / 3600, 1)

        # Calculate Current Streak
        # Logic: Consecutive days ending today or yesterday
        streak = 0
        date_stmt = select(func.date(UserAttempt.attempted_at)).where(UserAttempt.user_id == user_id).distinct()
        date_result = await self.repo.session.execute(date_stmt)
        # Dates come as date objects or strings depending on driver, usually date objects
        dates = sorted([r[0] for r in date_result.all()], reverse=True)
        
        if dates:
            today = date.today()
            yesterday = today - timedelta(days=1)
            
            # Check if streak is active (activity today or yesterday)
            if dates[0] == today or dates[0] == yesterday:
                streak = 1
                current_check = dates[0]
                
                # Iterate backwards to find consecutive days
                for i in range(1, len(dates)):
                    expected_prev = current_check - timedelta(days=1)
                    if dates[i] == expected_prev:
                        streak += 1
                        current_check = dates[i]
                    else:
                        break

        # Calculate Topic Performance (Heatmap)
        # Select Attempts + Question Data
        perf_stmt = select(UserAttempt, Question).join(Question, UserAttempt.question_id == Question.id).where(UserAttempt.user_id == user_id)
        perf_result = await self.repo.session.execute(perf_stmt)
        perf_rows = perf_result.all()

        topic_stats = {}  # {topic: {'correct': 0, 'total': 0}}
        topic_time_agg: dict[str, dict[str, float]] = {}  # topic -> sum/count
        concept_stats = {}  # {concept: {'correct': 0, 'total': 0}}

        total_attempt_rows = len(perf_rows)
        correct_attempt_rows = sum(1 for attempt, _q in perf_rows if attempt.is_correct)

        for attempt, question in perf_rows:
            # Safely extract topic
            topic = "General"
            concepts = []
            if question.tier_1_core_research:
                tags = question.tier_1_core_research.get("hierarchical_tags", {})
                if tags.get("topic"):
                    topic = tags["topic"].get("name") or "General"
                raw_concepts = tags.get("concepts") or []
                if isinstance(raw_concepts, list):
                    for c in raw_concepts:
                        if isinstance(c, dict) and c.get("name"):
                            concepts.append(str(c["name"]).strip())
                        elif isinstance(c, str) and c.strip():
                            concepts.append(c.strip())

            if topic not in topic_stats:
                topic_stats[topic] = {"correct": 0, "total": 0}

            topic_stats[topic]["total"] += 1
            if attempt.is_correct:
                topic_stats[topic]["correct"] += 1

            time_sec = float(attempt.time_taken_seconds or 0)
            if topic not in topic_time_agg:
                topic_time_agg[topic] = {"sum": 0.0, "count": 0.0}
            topic_time_agg[topic]["sum"] += time_sec
            topic_time_agg[topic]["count"] += 1.0

            # Attribute attempt to each tagged concept (same pattern as topic rollup)
            if not concepts:
                concepts = ["General"]
            for cn in concepts:
                if cn not in concept_stats:
                    concept_stats[cn] = {"correct": 0, "total": 0}
                concept_stats[cn]["total"] += 1
                if attempt.is_correct:
                    concept_stats[cn]["correct"] += 1

        # Calculate percentages
        topic_performance = {}
        for topic, counts in topic_stats.items():
            if counts["total"] > 0:
                topic_performance[topic] = round((counts["correct"] / counts["total"]) * 100, 1)

        topic_avg_time_seconds = {
            name: round(vals["sum"] / vals["count"], 1)
            for name, vals in topic_time_agg.items()
            if vals["count"] > 0
        }

        concept_performance = {}
        for cname, counts in concept_stats.items():
            if counts["total"] > 0:
                concept_performance[cname] = round((counts["correct"] / counts["total"]) * 100, 1)
        if len(concept_performance) > 50:
            concept_performance = dict(
                sorted(concept_performance.items(), key=lambda x: (x[1], x[0]))[:50]
            )

        percentage = 0.0
        if total_questions > 0:
            percentage = round((attempted_count / total_questions) * 100, 1)

        attempt_accuracy_pct = (
            round((correct_attempt_rows / total_attempt_rows) * 100, 1) if total_attempt_rows > 0 else 0.0
        )

        syllabus_tree = await self.get_syllabus_tree()
        syllabus_topic_catalog_total = sum(len(v) for v in syllabus_tree.values() if isinstance(v, list))
        if syllabus_topic_catalog_total <= 0:
            syllabus_topic_catalog_total = max(len(topic_stats.keys()), 1)

        topics_touched = len(topic_stats.keys())
        syllabus_progress = round(min(100.0, (topics_touched / syllabus_topic_catalog_total) * 100), 1)

        readiness_score = round(
            (attempt_accuracy_pct / 100.0) * (syllabus_progress / 100.0) * 100,
            1,
        )

        cutoff_7d = datetime.utcnow() - timedelta(days=7)
        attempts_7d_stmt = (
            select(func.count())
            .select_from(UserAttempt)
            .where(UserAttempt.user_id == user_id, UserAttempt.attempted_at >= cutoff_7d)
        )
        attempts_7d_result = await self.repo.session.execute(attempts_7d_stmt)
        attempts_last_7_days = int(attempts_7d_result.scalar() or 0)

        lite = compute_readiness_lite(
            attempt_accuracy_pct,
            syllabus_progress,
            target_band,
            attempts_last_7_days,
        )

        # Get Recent Activity
        recent_stmt = (
            select(UserAttempt, Question)
            .join(Question, UserAttempt.question_id == Question.id)
            .where(UserAttempt.user_id == user_id)
            .order_by(UserAttempt.attempted_at.desc())
            .limit(3)
        )
        recent_result = await self.repo.session.execute(recent_stmt)
        
        recent_activity_items = []
        for attempt, question in recent_result.all():
            q_text = question.question_text
            if len(q_text) > 100:
                q_text = q_text[:100] + "..."
                
            recent_activity_items.append({
                "question_id": question.question_id,
                "question_text": q_text,
                "is_correct": attempt.is_correct,
                "attempted_at": attempt.attempted_at
            })
            
        return DashboardStats(
            questions_attempted=attempted_count,
            attempt_percentage=percentage,
            hours_studied=hours_studied,
            time_studied_seconds=int(total_seconds),
            current_streak=streak,
            syllabus_progress=syllabus_progress,
            topic_performance=topic_performance,
            concept_performance=concept_performance,
            recent_activity=recent_activity_items,
            topic_avg_time_seconds=topic_avg_time_seconds,
            attempt_accuracy_pct=attempt_accuracy_pct,
            readiness_score=readiness_score,
            syllabus_topic_catalog_total=syllabus_topic_catalog_total,
            readiness_lite_pct=lite["readiness_lite_pct"],
            target_readiness_pct=lite["target_readiness_pct"],
            cutoff_gap_pct=lite["cutoff_gap_pct"],
            days_to_target_estimate=lite["days_to_target_estimate"],
            attempts_last_7_days=attempts_last_7_days,
        )

    async def record_attempt(self, user_id: int, question_id: str, is_correct: bool, time_taken: int) -> UserAttempt:
        """Record a user's attempt at a question."""
        
        # Convert string ID to UUID if needed, though we expect UUID here
        # If question_id is a string like "GATE...", we need to find its UUID
        try:
            q_uuid = uuid.UUID(question_id)
        except ValueError:
            q = await self.repo.get_by_question_id(question_id)
            if not q:
                raise ValueError("Question not found")
            q_uuid = q.id

        attempt = UserAttempt(
            user_id=user_id,
            question_id=q_uuid,
            is_correct=is_correct,
            time_taken_seconds=time_taken
        )
        self.repo.session.add(attempt)

        from app.domains.mistakes.models import UserMistakeAnnotation
        ann_stmt = select(UserMistakeAnnotation).where(
            UserMistakeAnnotation.user_id == user_id,
            UserMistakeAnnotation.question_uuid == q_uuid,
        )
        ann = (await self.repo.session.execute(ann_stmt)).scalar_one_or_none()
        now = datetime.utcnow()
        if ann is None:
            ann = UserMistakeAnnotation(
                user_id=user_id,
                question_uuid=q_uuid,
                wrong_count=0 if is_correct else 1,
                correct_count=1 if is_correct else 0,
                last_wrong_at=None if is_correct else now,
                last_correct_at=now if is_correct else None,
            )
            self.repo.session.add(ann)
        else:
            if is_correct:
                ann.correct_count = ann.correct_count + 1
                ann.last_correct_at = now
            else:
                ann.wrong_count = ann.wrong_count + 1
                ann.last_wrong_at = now
            self.repo.session.add(ann)

        await self.repo.session.commit()
        await self.repo.session.refresh(attempt)
        return attempt

    async def get_remediation_question_ids(self, user_id: int, limit: int = 25) -> list[dict]:
        """Distinct questions the user got wrong, most recently first."""
        subq = (
            select(
                UserAttempt.question_id.label("q_uuid"),
                func.max(UserAttempt.attempted_at).label("last_at"),
            )
            .where(UserAttempt.user_id == user_id)
            .where(UserAttempt.is_correct.is_(False))
            .group_by(UserAttempt.question_id)
            .subquery()
        )
        stmt = (
            select(Question.question_id, subq.c.last_at)
            .join(subq, Question.id == subq.c.q_uuid)
            .order_by(desc(subq.c.last_at))
            .limit(min(limit, 100))
        )
        result = await self.repo.session.execute(stmt)
        return [{"question_id": row[0], "last_wrong_at": row[1]} for row in result.all()]

    async def get_questions_by_string_ids(self, question_ids: list[str]) -> list[QuestionResponse]:
        rows = await self.repo.get_questions_by_string_ids(question_ids)
        return [QuestionResponse.model_validate(q) for q in rows]

    async def build_mock_paper(self, user_id: int, body: MockPaperRequest) -> list[str]:
        """Adaptive mock: weak topics + optional trap-heavy mix + random fill."""
        if body.seed is not None:
            random.seed(body.seed)
        stats = await self.get_user_dashboard_stats(user_id)
        tp = stats.topic_performance or {}
        weak_topics = [t for t, acc in sorted(tp.items(), key=lambda x: x[1]) if acc < 80][:12]
        qc = max(1, min(body.question_count, 100))
        trap_bias = max(0.0, min(body.trap_bias, 1.0))

        if weak_topics:
            n_weak = min(int(qc * 0.55), qc)
        else:
            n_weak = 0
        n_trap = min(int(qc * trap_bias), qc - n_weak)
        n_fill = qc - n_weak - n_trap

        chosen: list[str] = []
        seen: set[str] = set()

        def absorb(candidates: list[str]) -> None:
            for qid in candidates:
                if qid in seen:
                    continue
                chosen.append(qid)
                seen.add(qid)
                if len(chosen) >= qc:
                    break

        if n_weak > 0:
            pool = await self.repo.fetch_random_question_ids_from_topics(
                weak_topics, min(n_weak + 30, 500)
            )
            random.shuffle(pool)
            absorb(pool)

        if len(chosen) < qc and n_trap > 0:
            pool = await self.repo.fetch_random_trap_flag_question_ids(min(n_trap + 30, 500))
            random.shuffle(pool)
            absorb(pool)

        attempts = 0
        while len(chosen) < qc and attempts < 15:
            attempts += 1
            need = qc - len(chosen) + 20
            pool = await self.repo.fetch_random_question_ids(min(need, 500))
            random.shuffle(pool)
            absorb(pool)

        return chosen[:qc]

    @staticmethod
    def _collect_prerequisite_labels(tier1: Optional[dict]) -> list[str]:
        """Extract essential + helpful prerequisite strings; dedupe; cap 6."""
        if not tier1 or not isinstance(tier1, dict):
            return []
        prereq = tier1.get("prerequisites")
        if not prereq or not isinstance(prereq, dict):
            return []
        essential = prereq.get("essential") or []
        helpful = prereq.get("helpful") or []
        raw: list[str] = []
        for arr in (essential, helpful):
            if not isinstance(arr, list):
                continue
            for x in arr:
                if x is None:
                    continue
                s = str(x).strip()
                if s:
                    raw.append(s)
        seen: set[str] = set()
        out: list[str] = []
        for label in raw:
            key = label.lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(label)
            if len(out) >= 6:
                break
        return out

    async def gap_drill(self, question_id_str: str) -> Optional[GapDrillResponse]:
        """
        Build a warmup question list from tier_1 prerequisites via search (hybrid) per label.
        Excludes the source question; caps: 6 labels, 3 hits per label, 12 total IDs.
        """
        question = await self.repo.get_by_question_id(question_id_str)
        if not question:
            return None
        tier1 = question.tier_1_core_research
        labels = self._collect_prerequisite_labels(tier1 if isinstance(tier1, dict) else None)
        if not labels:
            return None

        collected: list[str] = []
        seen_ids: set[str] = set()

        for label in labels:
            rows, _total = await self.repo.search(label, None, page=1, page_size=3)
            for row in rows:
                qid = row.question_id
                if qid == question_id_str or qid in seen_ids:
                    continue
                collected.append(qid)
                seen_ids.add(qid)
                if len(collected) >= 12:
                    break
            if len(collected) >= 12:
                break

        return GapDrillResponse(
            original_question_id=question_id_str,
            prerequisite_labels=labels,
            question_ids=collected,
            total_found=len(collected),
        )


