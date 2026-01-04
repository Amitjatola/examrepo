"""
Search API endpoint for concept-based question search.
This is the main entry point for the homepage search functionality.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_session
from app.domains.questions.service import QuestionService
from app.domains.questions.schemas import SearchResult, FilterOptions, SearchFilters


router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResult)
@router.get("", response_model=SearchResult)
async def search_questions(
    q: Optional[str] = Query(None, description="Search query - concept, topic, or keyword"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),
    year: Optional[int] = Query(None, description="Filter by exam year"),
    years: Optional[str] = Query(None, description="Filter by multiple years (comma-separated)"),
    subject: Optional[str] = Query(None, description="Filter by subject"),
    topic: Optional[str] = Query(None, description="Filter by exact topic"),
    question_type: Optional[str] = Query(None, description="MCQ or NAT"),
    difficulty_min: Optional[int] = Query(None, ge=1, le=10, description="Minimum difficulty"),
    difficulty_max: Optional[int] = Query(None, ge=1, le=10, description="Maximum difficulty"),
    session: AsyncSession = Depends(get_session),
):
    """
    Search questions by concept, topic, or keyword.
    
    This is the main search endpoint for the homepage.
    Searches across:
    - Question text
    - Search keywords (from tier_3)
    - Concepts (from tier_1)
    
    Returns paginated results with metadata for display.
    """
    service = QuestionService(session)
    
    # Parse years if provided as comma-separated string
    years_list = None
    if years:
        try:
            years_list = [int(y.strip()) for y in years.split(",")]
        except ValueError:
            pass
    
    filters = SearchFilters(
        year=year,
        years=years_list,
        subject=subject,
        topic=topic,
        question_type=question_type,
        difficulty_min=difficulty_min,
        difficulty_max=difficulty_max,
    )
    
    # Ensure at least one filter or query is present
    if not q and not (year or years or subject or topic or question_type):
        # Fallback to empty result if nothing provided to prevent full DB dump if that was the intention
        # Or maybe we allow listing all questions? Current repo implementation lists all if !query.
        pass
    
    result = await service.search_questions(q or "", filters, page, page_size)
    return result


@router.get("/filters", response_model=FilterOptions)
async def get_filter_options(
    session: AsyncSession = Depends(get_session),
):
    """
    Get available filter options for the search UI.
    
    Returns:
    - Available years
    - Available subjects
    - Available topics
    - Available question types
    - Available concepts
    """
    service = QuestionService(session)
    return await service.get_filter_options()


@router.get("/suggestions", response_model=list[str])
async def get_search_suggestions(
    q: str = Query(..., min_length=2, description="Partial search query"),
    limit: int = Query(5, ge=1, le=20, description="Max suggestions"),
    session: AsyncSession = Depends(get_session),
):
    """
    Get autocomplete suggestions for the search box.
    Returns concept names and keywords that match the partial query.
    Utilizes pg_trgm for fuzzy matching and typo tolerance.
    """
    repo = QuestionService(session).repo
    suggestions = await repo.get_suggestions(q, limit)
    return suggestions


@router.get("/year-counts", response_model=dict[int, int])
async def get_year_counts(
    session: AsyncSession = Depends(get_session),
):
    """
    Get question counts grouped by year.
    Returns a dictionary mapping year -> count for displaying in the year selection UI.
    """
    repo = QuestionService(session).repo
    return await repo.get_year_counts()

