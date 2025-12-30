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
)
from app.domains.questions.models import Question


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
        difficulty_score = None
        if question.tier_0_classification:
            difficulty_score = question.tier_0_classification.get("difficulty_score")
        
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
            subject=question.subject,
            question_text=question.question_text[:1000] if len(question.question_text) > 1000 else question.question_text,
            question_type=question.question_type,
            marks=question.marks,
            difficulty_score=difficulty_score,
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
