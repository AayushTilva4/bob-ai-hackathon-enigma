"""
pytest fixtures shared across all tests.

Uses an in-memory SQLite database so tests run without a live PostgreSQL instance.
Seed builders are called directly to avoid monkey-patching the seed module.

SQLite + SQLAlchemy 2.0 note: we insert records one at a time to avoid the
insertmanyvalues RETURNING path which conflicts with explicit UUID PKs on SQLite.
"""

import asyncio
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.connection import get_db
from database.models import Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
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


async def _add_one_by_one(session: AsyncSession, items: list) -> None:
    """Insert items individually to avoid SQLite insertmanyvalues RETURNING issues."""
    for item in items:
        session.add(item)
        await session.flush()


@pytest_asyncio.fixture(scope="session")
async def seeded_app(test_session_factory):
    """
    Return the FastAPI app wired to the test DB, with seed data inserted.
    Seed builders are called directly; records inserted individually.
    """
    import main as app_module
    from seed.seed_data import (
        _build_berths,
        _build_cranes,
        _build_yard_zones,
        _build_routes,
        _build_vessels,
        _build_schedules,
        _build_port_state,
    )

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with test_session_factory() as session:
            yield session

    app_module.app.dependency_overrides[get_db] = override_get_db

    async with test_session_factory() as session:
        berths = _build_berths()
        await _add_one_by_one(session, berths)

        cranes = _build_cranes(berths)
        yard_zones = _build_yard_zones()
        routes = _build_routes()
        await _add_one_by_one(session, cranes)
        await _add_one_by_one(session, yard_zones)
        await _add_one_by_one(session, routes)

        vessels = _build_vessels(berths)
        await _add_one_by_one(session, vessels)

        schedules = _build_schedules(vessels, berths, yard_zones, routes)
        port_state = _build_port_state(vessels, berths)
        await _add_one_by_one(session, schedules)
        session.add(port_state)
        await session.commit()

    return app_module.app


@pytest_asyncio.fixture(scope="session")
async def client(seeded_app) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=seeded_app), base_url="http://test"
    ) as ac:
        yield ac
