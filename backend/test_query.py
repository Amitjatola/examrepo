import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, and_, func
from app.domains.questions.models import Question

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/aerogate"

async def main():
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        topic = "Aerodynamic Characteristics"
        conditions = [
            Question.tier_1_core_research['hierarchical_tags', 'topic', 'name'].astext == topic
        ]
        stmt = select(Question).order_by(Question.year.desc()).where(and_(*conditions))
        try:
            res = await session.execute(stmt)
            print("OK")
        except Exception as e:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
