
import asyncio
import sys
import json
from pathlib import Path

# Add the parent directory to sys.path to import app modules
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import async_session_maker
from app.domains.questions.repository import QuestionRepository
from app.domains.questions.schemas import QuestionCreate

async def import_question(file_path: str):
    print(f"🚀 Starting import from {file_path}...")
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        async with async_session_maker() as session:
            repo = QuestionRepository(session)
            
            # Validate with schema
            question_data = QuestionCreate(**data)
            
            # Check if exists
            existing = await repo.get_by_question_id(question_data.question_id)
            if existing:
                print(f"⚠️ Question {question_data.question_id} already exists. Skipping.")
                return

            # Create
            question = await repo.create(question_data)
            await session.commit()
            print(f"✅ Successfully imported question: {question.question_id} ({question.year})")
            
    except Exception as e:
        print(f"❌ Error importing question: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_single.py <path_to_json_file>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    asyncio.run(import_question(file_path))
