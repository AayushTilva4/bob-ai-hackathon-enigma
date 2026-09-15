"""
HarborAI — FastAPI application entry point.
"""

import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api import berths, copilot, cranes, health, optimization, port, prediction, routes, simulation, vessels, yard
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
        try:
            await seed_if_empty()
        except Exception as exc:
            logger.warning(
                "Could not initialize seed data on startup (PostgreSQL may be offline or unmigrated): %s",
                exc,
            )
    yield
    # Shutdown
    try:
        await engine.dispose()
    except Exception as exc:
        logger.warning("Error disposing database engine on shutdown: %s", exc)
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


from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    code = "NOT_FOUND" if exc.status_code == 404 else f"HTTP_{exc.status_code}"
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail), "code": code},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"detail": "Invalid request parameters or payload", "code": "VALIDATION_ERROR"},
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
app.include_router(simulation.router)
app.include_router(prediction.router)
app.include_router(optimization.router)
app.include_router(copilot.router)


# ---------------------------------------------------------------------------
# CORS — allow frontend to call backend
# ---------------------------------------------------------------------------

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
