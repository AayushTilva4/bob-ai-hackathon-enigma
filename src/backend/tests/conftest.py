"""
Pytest fixtures shared across all tests.

Integration tests run against the PostgreSQL database configured via environment.
"""

import os
import subprocess
import sys
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from database.connection import get_db

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")
load_dotenv(REPO_ROOT / "src" / "backend" / ".env")

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    os.getenv("DATABASE_URL", "postgresql+asyncpg://harborai:harborai@localhost:5432/harborai_test"),
)
TEST_DATABASE_URL_SYNC = os.getenv(
    "TEST_DATABASE_URL_SYNC",
    os.getenv("DATABASE_URL_SYNC", TEST_DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)),
)


def _run_alembic(*args: str) -> None:
    env = os.environ.copy()
    env["TEST_DATABASE_URL_SYNC"] = TEST_DATABASE_URL_SYNC
    subprocess.run(
        [sys.executable, "-m", "alembic", "-c", str(REPO_ROOT / "alembic.ini"), *args],
        cwd=REPO_ROOT,
        env=env,
        check=True,
    )


@pytest.fixture(scope="session", autouse=True)
def run_migrations():
    _run_alembic("upgrade", "head")


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    import main as app_module
    import seed.seed_data as seed_module

    test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    app_module.app.dependency_overrides[get_db] = override_get_db

    # Ensure seeded data is present
    original_session_factory = seed_module.AsyncSessionLocal
    seed_module.AsyncSessionLocal = session_factory
    try:
        await seed_module.seed_if_empty()
    finally:
        seed_module.AsyncSessionLocal = original_session_factory

    async with AsyncClient(
        transport=ASGITransport(app=app_module.app), base_url="http://test"
    ) as ac:
        yield ac

    await test_engine.dispose()
