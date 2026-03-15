import asyncio
from sqlmodel import select, func
from app.core.database import async_session_maker
from app.domains.questions.models import Question

async def check_count():
    async with async_session_maker() as session:
        result = await session.execute(select(func.count(Question.id)))
        count = result.scalar()
        print(f"Total questions in DB: {count}")

if __name__ == "__main__":
    asyncio.run(check_count())
