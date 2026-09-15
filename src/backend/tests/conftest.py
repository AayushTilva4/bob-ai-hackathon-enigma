"""
Pytest fixtures shared across all tests.

Integration tests run against the dedicated PostgreSQL test database and build
the schema through the real Alembic migration path.
"""

import asyncio
import os
import subprocess
import sys
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.connection import get_db
from database.models import Base

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://harborai:harborai@localhost:5432/harborai_test",
)
TEST_DATABASE_URL_SYNC = os.getenv(
    "TEST_DATABASE_URL_SYNC",
    TEST_DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1),
)
REPO_ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


def _run_alembic(*args: str) -> None:
    env = os.environ.copy()
    env["TEST_DATABASE_URL_SYNC"] = TEST_DATABASE_URL_SYNC
    subprocess.run(
        [sys.executable, "-m", "alembic", "-c", str(REPO_ROOT / "alembic.ini"), *args],
        cwd=REPO_ROOT,
        env=env,
        check=True,
    )


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Make the test database empty, then create it exactly as production does.
    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))

    _run_alembic("upgrade", "head")

    yield engine

    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def test_session_factory(test_engine):
    return async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )


@pytest_asyncio.fixture(scope="session")
async def seeded_app(test_session_factory):
    """Return the FastAPI app wired to the migrated test DB and real seed routine."""
    import main as app_module
    import seed.seed_data as seed_module

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with test_session_factory() as session:
            yield session

    app_module.app.dependency_overrides[get_db] = override_get_db

    # Reuse the production seed routine, but temporarily point its session factory
    # at the isolated integration-test database.
    original_session_factory = seed_module.AsyncSessionLocal
    seed_module.AsyncSessionLocal = test_session_factory
    try:
        await seed_module.seed_if_empty()
    finally:
        seed_module.AsyncSessionLocal = original_session_factory

    return app_module.app


@pytest_asyncio.fixture(scope="session")
async def client(seeded_app) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=seeded_app), base_url="http://test"
    ) as ac:
        yield ac
