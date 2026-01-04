
import asyncio
from sqlalchemy import select
from app.core.database import get_session_context
from app.domains.questions.models import Question

async def inspect_2018_duplicates():
    async with get_session_context() as session:
        print("Inspecting Duplicates in 2018...")
        
        # Get collisions
        stmt = select(Question).where(Question.year == 2018).where(Question.question_number.in_([4, 10, 9, 7, 6, 3, 1, 5, 2, 8])).order_by(Question.question_number)
        result = await session.execute(stmt)
        questions = result.scalars().all()
        
        for q in questions:
            print(f"Num: {q.question_number} | ID: {q.question_id} | Subject: {q.subject}")

if __name__ == "__main__":
    asyncio.run(inspect_2018_duplicates())
