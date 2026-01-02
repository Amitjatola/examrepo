"""
Question service for business logic.
Orchestrates between API and repository layers.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

from app.domains.questions.repository import QuestionRepository
from app.domains.questions.schemas import (
    QuestionCreate,
    QuestionResponse,
    QuestionListItem,
    SearchFilters,
    SearchResult,
    FilterOptions,
    DashboardStats,
)
from app.domains.questions.models import Question, UserAttempt


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

    async def get_user_dashboard_stats(self, user_id: int) -> DashboardStats:
        """Calculate dashboard statistics for a user."""
        # This belongs in a repo, but for now we put it here or access a new repo
        # To avoid circular imports or complexity, we'll do a direct query for now
        # Ideally we should have a UserAttemptRepository
        
        from sqlalchemy import select, func
        from app.domains.questions.models import UserAttempt, Question
        
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
            from datetime import date, timedelta
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
        
        topic_stats = {} # {topic: {'correct': 0, 'total': 0}}
        
        for attempt, question in perf_result.all():
            # Safely extract topic
            topic = "General"
            if question.tier_1_core_research:
                tags = question.tier_1_core_research.get("hierarchical_tags", {})
                if tags.get("topic"):
                    topic = tags["topic"].get("name") or "General"
            
            if topic not in topic_stats:
                topic_stats[topic] = {'correct': 0, 'total': 0}
            
            topic_stats[topic]['total'] += 1
            if attempt.is_correct:
                topic_stats[topic]['correct'] += 1
        
        # Calculate percentages
        topic_performance = {}
        for topic, counts in topic_stats.items():
            if counts['total'] > 0:
                topic_performance[topic] = round((counts['correct'] / counts['total']) * 100, 1)

        percentage = 0.0
        if total_questions > 0:
            percentage = round((attempted_count / total_questions) * 100, 1)
            
        return DashboardStats(
            questions_attempted=attempted_count,
            attempt_percentage=percentage,
            hours_studied=hours_studied,
            time_studied_seconds=int(total_seconds),
            current_streak=streak,
            syllabus_progress=0.0,  # Placeholder for future implementation
            topic_performance=topic_performance
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
        await self.repo.session.commit()
        await self.repo.session.refresh(attempt)
        return attempt


