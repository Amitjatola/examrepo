"""
Database initialization script - creates all tables including subscriptions.
Run this after updating models to create new tables.
"""
import asyncio
from app.core.database import init_db

async def main():
    print("Creating database tables...")
    await init_db()
    print("✅ Database tables created successfully!")
    print("   - users")
    print("   - questions")
    print("   - user_attempts")
    print("   - user_subscriptions (NEW)")

if __name__ == "__main__":
    asyncio.run(main())
