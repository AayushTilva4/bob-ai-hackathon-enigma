"""
pytest fixtures shared across all tests.

Uses the dedicated PostgreSQL integration-test database.  The production schema
uses PostgreSQL UUID columns, so exercising the API against PostgreSQL prevents
SQLite type-affinity differences from masking or creating database bugs.
"""

import asyncio
import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.connection import get_db
from database.models import Base

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://harborai:harborai@localhost:5432/harborai_test",
)


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
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
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
    """
    Return the FastAPI app wired to the test DB, with seed data inserted once.
    Seed builders are called directly so application startup never touches the
    production-session dependency during a test run.
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
        session.add_all(berths)
        await session.flush()

        cranes = _build_cranes(berths)
        yard_zones = _build_yard_zones()
        routes = _build_routes()
        session.add_all(cranes)
        session.add_all(yard_zones)
        session.add_all(routes)
        await session.flush()

        vessels = _build_vessels(berths)
        session.add_all(vessels)
        await session.flush()

        schedules = _build_schedules(vessels, berths, yard_zones, routes)
        port_state = _build_port_state(vessels, berths)
        session.add_all(schedules)
        session.add(port_state)
        await session.commit()

    return app_module.app


@pytest_asyncio.fixture(scope="session")
async def client(seeded_app) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=seeded_app), base_url="http://test"
    ) as ac:
        yield ac
