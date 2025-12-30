"""
Question API endpoints for CRUD operations.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import json
import uuid

from app.core.database import get_session
from app.domains.questions.service import QuestionService
from app.domains.questions.schemas import QuestionResponse, SearchFilters


router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("", response_model=list[QuestionResponse])
async def list_questions(
    page: int = 1,
    page_size: int = 20,
    year: Optional[int] = None,
    subject: Optional[str] = None,
    question_type: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
):
    """
    List questions with optional filters.
    Returns paginated results.
    """
    service = QuestionService(session)
    filters = SearchFilters(year=year, subject=subject, question_type=question_type)
    result = await service.search_questions("", filters, page, page_size)
    
    # Return full question data for list endpoint
    full_questions = []
    for item in result.questions:
        q = await service.get_question(item.id)
        if q:
            full_questions.append(q)
    
    return full_questions


@router.get("/syllabus", response_model=dict)
async def get_syllabus(
    session: AsyncSession = Depends(get_session),
):
    """
    Get the full syllabus tree (Subject -> Topics).
    Used for the Syllabus drill-down navigation.
    """
    service = QuestionService(session)
    return await service.get_syllabus_tree()


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Get a single question by ID.
    Accepts both UUID and string ID (e.g., GATE_AE_2008_Q01).
    """
    service = QuestionService(session)
    
    # Try as UUID first
    try:
        uuid_id = uuid.UUID(question_id)
        question = await service.get_question(uuid_id)
    except ValueError:
        # Not a UUID, try as string ID
        question = await service.get_question_by_string_id(question_id)
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return question


@router.post("/import", response_model=dict)
async def import_question(
    question_data: dict,
    session: AsyncSession = Depends(get_session),
):
    """
    Import a single question from JSON data.
    Used for adding new questions to the database.
    """
    service = QuestionService(session)
    try:
        result = await service.import_question(question_data)
        return {"message": "Question imported successfully", "question_id": result.question_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/import/bulk", response_model=dict)
async def bulk_import_questions(
    file: UploadFile = File(..., description="JSON file containing array of questions"),
    session: AsyncSession = Depends(get_session),
):
    """
    Bulk import questions from a JSON file.
    Expects an array of question objects or a single question object.
    """
    service = QuestionService(session)
    
    try:
        content = await file.read()
        data = json.loads(content)
        
        # Handle both single question and array
        if isinstance(data, list):
            questions_data = data
        else:
            questions_data = [data]
        
        result = await service.bulk_import(questions_data)
        return {
            "message": "Import complete",
            "imported": result["imported"],
            "total_in_db": result["total_in_db"],
        }
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
