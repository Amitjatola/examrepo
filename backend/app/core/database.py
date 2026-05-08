"""
Database connection and session management.
Uses SQLModel with async PostgreSQL driver.
"""

from sqlmodel import SQLModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from app.core.config import settings
# Import all models here to ensure they are registered with SQLModel metadata before create_all is called
from app.domains.questions.models import Question, UserAttempt, UserQuestionBookmark
from app.domains.auth.models import User
from app.domains.subscriptions.models import UserSubscription
from app.domains.discussions.models import Discussion
from app.domains.revisions.models import UserQuestionRevision
from app.domains.mistakes.models import UserMistakeAnnotation


from sqlalchemy.pool import NullPool

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
    poolclass=NullPool,  # Critical for Lambda: Disable pooling to avoid frozen/stale connections
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def _ensure_users_leaderboard_columns(conn) -> None:
    """
    create_all() does not add columns to existing tables.
    Older Postgres DBs need these for User model + superuser seed.
    Idempotent: IF NOT EXISTS (PG 9.1+ ADD COLUMN IF NOT EXISTS in PG 11+).
    """
    # SQLite uses IF NOT EXISTS on ADD COLUMN from 3.x; Postgres 11+
    await conn.execute(
        text(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS leaderboard_alias VARCHAR(64)"
        )
    )
    await conn.execute(
        text(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS leaderboard_visibility VARCHAR(20) DEFAULT 'anonymous'"
        )
    )


async def init_db() -> None:
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        await _ensure_users_leaderboard_columns(conn)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_session_context() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for database session (for non-FastAPI usage)."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
