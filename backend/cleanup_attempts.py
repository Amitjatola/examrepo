
import asyncio
from sqlalchemy import delete, select
from app.core.database import get_session_context
from app.domains.questions.models import UserAttempt, Question

async def cleanup_attempts():
    async with get_session_context() as session:
        print("Cleaning up ghost attempts for User ID 6...")
        
        # identifying questions with those topics first to be safe, or just delete by user_id
        # attempting strict cleanup for the specific user and topics
        
        stmt = select(UserAttempt).join(Question).where(
             UserAttempt.user_id == 6
        )
        
        # We can also just delete all attempts for user 6 if they want a clean slate, 
        # but let's be surgical.
        # Actually, if the user says "I haven't started", they probably want 0 stats.
        # Let's delete ALL attempts for User 6.
        
        del_stmt = delete(UserAttempt).where(UserAttempt.user_id == 6)
        result = await session.execute(del_stmt)
        await session.commit()
        
        print(f"Deleted {result.rowcount} attempts for User ID 6.")

if __name__ == "__main__":
    asyncio.run(cleanup_attempts())
