"""
Script to re-index all existing questions in the database.
Generates 'Content Soup' and Vector Embeddings using BBA/bge-large-en-v1.5.
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to sys.path to import app modules
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import async_session_maker
from app.domains.questions.repository import QuestionRepository
from app.domains.questions.models import Question
from sqlalchemy import select

async def reindex():
    print("🚀 Starting re-indexing process...")
    async with async_session_maker() as session:
        repo = QuestionRepository(session)
        
        # Get all questions
        result = await session.execute(select(Question))
        questions = result.scalars().all()
        print(f"📦 Found {len(questions)} questions to re-index.")
        
        count = 0
        for q in questions:
            print(f"🔄 Processing {q.question_id}...")
            
            # Use the same logic as the repository for consistency
            data_dict = {
                "question_text": q.question_text,
                "tier_1_core_research": q.tier_1_core_research,
                "tier_3_enhanced_learning": q.tier_3_enhanced_learning
            }
            
            content, embedding = repo._prepare_search_data(data_dict)
            
            q.search_content = content
            q.embedding = embedding
            count += 1
            
        await session.commit()
        print(f"✅ Successfully re-indexed {count} questions.")

if __name__ == "__main__":
    asyncio.run(reindex())
