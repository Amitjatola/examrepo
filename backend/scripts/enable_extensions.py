import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Default to argument
if len(sys.argv) > 1:
    DB_URL = sys.argv[1]
else:
    print("❌ Error: No DATABASE_URL provided.")
    sys.exit(1)

async def enable_extensions():
    print(f"🔌 Connecting to Database to enable extensions...")
    # Use postgres database to enable extensions if possible, or the target db
    engine = create_async_engine(DB_URL, echo=True)
    
    try:
        async with engine.begin() as conn:
            print("Activating pg_trgm...")
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
            print("Activating vector...")
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            print("✅ Extensions enabled successfully!")
            
    except Exception as e:
        print(f"❌ Error enabling extensions: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(enable_extensions())
