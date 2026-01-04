"""
Pydantic schemas for Question API request/response.
Separate from SQLModel to allow different shapes for API vs DB.
"""

from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
import uuid
from app.schemas.analytics import (
    Tier0Classification,
    Tier1CoreResearch,
    Tier2StudentLearning,
    Tier3EnhancedLearning,
    Tier4Metadata
)


# ============== Request Schemas ==============

class QuestionCreate(BaseModel):
    """Schema for creating a question from JSON import."""
    question_id: str
    exam_name: str = "GATE"
    subject: str
    year: int
    question_number: int
    question_text: str
    question_text_latex: Optional[str] = None
    question_type: str
    marks: float = 1.0
    negative_marks: float = 0.33
    options: Optional[dict] = None
    answer_key: str
    has_question_image: bool = False
    image_metadata: Optional[dict] = None
    tier_0_classification: Optional[Tier0Classification] = None
    tier_1_core_research: Optional[Tier1CoreResearch] = None
    tier_2_student_learning: Optional[Tier2StudentLearning] = None
    tier_3_enhanced_learning: Optional[Tier3EnhancedLearning] = None
    tier_4_metadata: Optional[Tier4Metadata] = None


class SearchFilters(BaseModel):
    """Filters for question search."""
    year: Optional[int] = None
    years: Optional[list[int]] = Field(default=None, description="Filter by multiple years")
    subject: Optional[str] = None
    topic: Optional[str] = None
    question_type: Optional[str] = Field(default=None, description="MCQ or NAT")
    difficulty_min: Optional[int] = Field(default=None, ge=1, le=10)
    difficulty_max: Optional[int] = Field(default=None, ge=1, le=10)
    concepts: Optional[list[str]] = Field(default=None, description="Filter by concept names")


# ============== Response Schemas ==============

class QuestionListItem(BaseModel):
    """Lightweight question for list/search results."""
    id: uuid.UUID
    question_id: str
    year: int
    question_number: int
    subject: str
    question_text: str
    question_text_latex: Optional[str] = None
    question_type: str
    marks: float
    difficulty_score: Optional[int] = None
    difficulty_level: Optional[str] = "Medium" # Default to Medium if unknown
    topic: Optional[str] = None
    concepts: list[str] = []
    options: Optional[dict] = None
    answer_key: Optional[str] = None
    explanation: Optional[dict] = None
    
    class Config:
        from_attributes = True


class QuestionResponse(BaseModel):
    """Full question response with all tier data."""
    id: uuid.UUID
    question_id: str
    exam_name: str
    subject: str
    year: int
    question_number: int
    question_text: str
    question_text_latex: Optional[str]
    question_type: str
    marks: float
    negative_marks: float
    options: Optional[dict]
    answer_key: str
    has_question_image: bool
    image_metadata: Optional[dict]
    tier_0_classification: Optional[Tier0Classification]
    tier_1_core_research: Optional[Tier1CoreResearch]
    tier_2_student_learning: Optional[Tier2StudentLearning]
    tier_3_enhanced_learning: Optional[Tier3EnhancedLearning]
    tier_4_metadata: Optional[Tier4Metadata]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SearchResult(BaseModel):
    """Search results with pagination."""
    query: str
    total: int
    page: int
    page_size: int
    filters_applied: dict
    questions: list[QuestionListItem]


class FilterOptions(BaseModel):
    """Available filter options for the search UI."""
    years: list[int]
    subjects: list[str]
    topics: list[str]
    question_types: list[str]
    concepts: list[str]


class DashboardStats(BaseModel):
    """Stats for user dashboard."""
    questions_attempted: int
    attempt_percentage: float
    hours_studied: float
    time_studied_seconds: int = 0
    current_streak: int
    syllabus_progress: float = 0.0
    topic_performance: dict[str, float] = {}
    # Future fields can be added here


class AttemptRequest(BaseModel):
    """Request schema for recording an attempt."""
    is_correct: bool
    time_taken_seconds: int = 0


