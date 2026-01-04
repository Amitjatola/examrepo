"""
Question database model using SQLModel.
Stores the rich JSON data structure with PostgreSQL JSONB columns.
"""

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Text, JSON
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
from typing import Optional, List
from datetime import datetime
import uuid


class Question(SQLModel, table=True):
    """
    Question model storing GATE Aerospace exam questions.
    Uses JSON columns for the rich tier data to enable flexible querying.
    """
    __tablename__ = "questions"
    
    # Primary key
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    # Core identifiers
    question_id: str = Field(unique=True, index=True, description="e.g., GATE_AE_2008_Q01")
    exam_name: str = Field(default="GATE", index=True)
    subject: str = Field(index=True, description="e.g., Aerospace Engineering")
    year: int = Field(index=True, description="Exam year")
    question_number: int
    
    # Question content
    question_text: str = Field(sa_column=Column(Text))
    question_text_latex: Optional[str] = Field(default=None, sa_column=Column(Text))
    question_type: str = Field(index=True, description="MCQ or NAT")
    marks: float = Field(default=1.0)
    negative_marks: float = Field(default=0.33)
    
    # Options and answer (for MCQ)
    options: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    answer_key: str
    
    # Image metadata
    has_question_image: bool = Field(default=False)
    image_metadata: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    
    # Tier data stored as JSON for flexible querying
    tier_0_classification: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    tier_1_core_research: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    tier_2_student_learning: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    tier_3_enhanced_learning: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    tier_4_metadata: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    
    # Search Optimization Fields
    search_content: Optional[str] = Field(default=None, sa_column=Column(Text))
    embedding: Optional[List[float]] = Field(default=None, sa_column=Column(Vector(384)))
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "question_id": "GATE_AE_2008_Q01",
                "subject": "Aerospace Engineering",
                "year": 2008,
                "question_type": "MCQ",
                "marks": 1.0,
            }
        }


class UserAttempt(SQLModel, table=True):
    """
    Tracks a user's attempt at a question.
    """
    __tablename__ = "user_attempts"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    question_id: uuid.UUID = Field(index=True)
    is_correct: bool = Field(default=False)
    time_taken_seconds: int = Field(default=0)
    attempted_at: datetime = Field(default_factory=datetime.utcnow)

