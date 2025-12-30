import asyncio
import os
import sys
# Add backend directory to python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
# Import all models to register them
from app.domains.questions.models import Question
# from app.domains.auth.models import User # User model might not exist or be imported yet if I check schemas

# Default to env var or argument
if len(sys.argv) > 1:
    DB_URL = sys.argv[1]
else:
    # Placeholder or env var
    DB_URL = os.getenv("DATABASE_URL", "")

if not DB_URL:
    print("❌ Error: No DATABASE_URL provided. Pass it as an argument or set the environment variable.")
    print("Usage: python3 backend/scripts/init_remote_db.py <DATABASE_URL>")
    sys.exit(1)

async def init_remote():
    print(f"Connecting to {DB_URL}...")
    try:
        engine = create_async_engine(DB_URL)
        async with engine.begin() as conn:
            # Create extension if not exists
            from sqlalchemy import text
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            print("Creating tables...")
            await conn.run_sync(SQLModel.metadata.create_all)
        print("✅ Tables created successfully!")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(init_remote())
