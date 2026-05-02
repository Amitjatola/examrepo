"""Test configuration and fixtures."""
import pytest
import asyncio
import os
from typing import AsyncGenerator
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.core.database import get_session
# Register all SQLModel tables (including user_question_bookmarks) on metadata
import app.core.database  # noqa: F401

# Test database URL (use separate test database). Override with env for CI/local.
TEST_DATABASE_URL = os.environ.get(
    "AEROGATE_TEST_DATABASE_URL",
    "postgresql+asyncpg://amitjatola@localhost:5432/aerogate_test",
)

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    yield engine
    
    # Drop all tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture
async def session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def async_client(session) -> AsyncGenerator[AsyncClient, None]:
    """HTTP client against the FastAPI app with DB session override."""

    async def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()
