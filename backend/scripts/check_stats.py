import asyncio
import sys
import os
from sqlmodel import select, func
from sqlalchemy.ext.asyncio import create_async_engine
from app.domains.questions.models import Question

# Default to argument
if len(sys.argv) > 1:
    DB_URL = sys.argv[1]
else:
    print("❌ Error: No DATABASE_URL provided.")
    sys.exit(1)

async def check_stats():
    print(f"Connecting to Database...")
    engine = create_async_engine(DB_URL, echo=False)
    
    try:
        async with engine.connect() as conn:
            # Check Questions
            result = await conn.execute(select(func.count()).select_from(Question))
            count = result.scalar()
            print(f"📊 Question Count: {count}")
            
            if count == 0:
                print("ℹ️  The table is empty. (This is expected, we haven't migrated data yet).")
            else:
                print("✅ Data is present.")
                
    except Exception as e:
        print(f"❌ Error reading database: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_stats())
