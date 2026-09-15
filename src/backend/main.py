"""
HarborAI — FastAPI application entry point.
"""

import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api import health, vessels, berths, cranes, yard, routes, port
from config import get_settings
from database.connection import engine
from seed.seed_data import seed_if_empty

settings = get_settings()
logging.basicConfig(level=settings.log_level.upper())
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    logger.info("HarborAI backend starting (env=%s)", settings.environment)
    if settings.seed_db:
        await seed_if_empty()
    yield
    # Shutdown
    await engine.dispose()
    logger.info("HarborAI backend stopped")


app = FastAPI(
    title="HarborAI",
    description="Intelligent Port Operations Optimizer — IBM BoB Hackathon 2026",
    version=settings.version,
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found", "code": "NOT_FOUND"},
    )


@app.exception_handler(500)
async def server_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled server error")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "code": "INTERNAL_ERROR"},
    )


# ---------------------------------------------------------------------------
# Routers — all under /api
# ---------------------------------------------------------------------------

app.include_router(health.router, prefix="/api")
app.include_router(vessels.router, prefix="/api")
app.include_router(berths.router, prefix="/api")
app.include_router(cranes.router, prefix="/api")
app.include_router(yard.router, prefix="/api")
app.include_router(routes.router, prefix="/api")
app.include_router(port.router, prefix="/api")
