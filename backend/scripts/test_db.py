import asyncio
import sys
import os

# Add parent directory to path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.database import init_db, engine
from app.domains.auth.models import User
from sqlalchemy import text

async def main():
    print(f"Testing DB Connection...")
    print(f"URL: {settings.database_url}")
    
    try:
        # Try to initialize DB (create tables)
        print("Initializing DB (creating tables)...")
        await init_db()
        print("DB Initialized.")
        
        # Try a simple query
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print(f"Query Result: {result.scalar()}")

        # Test User Creation flow
        from app.domains.auth import services
        from app.domains.auth.schemas import UserCreate
        from app.core.database import get_session_context
        
        print("Testing User Creation...")
        async with get_session_context() as session:
            test_email = "script_test_user@example.com"
            # Cleanup first
            from app.domains.auth.models import User
            from sqlalchemy import delete
            await session.execute(delete(User).where(User.email == test_email))
            await session.commit()
            
            user_in = UserCreate(email=test_email, password="password", full_name="Script User")
            user = await services.create_user(session, user_in)
            print(f"User Created: {user.id} - {user.email}")
            
        print("SUCCESS: Database and Auth Services are working.")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
