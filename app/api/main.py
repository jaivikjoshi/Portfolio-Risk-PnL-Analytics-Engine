from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import (
    benchmark,
    dashboard,
    exposures,
    health,
    ingestion,
    pnl,
    positions,
    returns,
    risk,
    snapshots,
    validation,
)
from app.core.config import settings
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Portfolio reporting, PnL, exposure, validation, and risk analytics API.",
        lifespan=lifespan,
    )

    app.include_router(health.router)
    app.include_router(ingestion.router, prefix="/api/v1")
    app.include_router(validation.router, prefix="/api/v1")
    app.include_router(positions.router, prefix="/api/v1")
    app.include_router(pnl.router, prefix="/api/v1")
    app.include_router(returns.router, prefix="/api/v1")
    app.include_router(exposures.router, prefix="/api/v1")
    app.include_router(risk.router, prefix="/api/v1")
    app.include_router(benchmark.router, prefix="/api/v1")
    app.include_router(snapshots.router, prefix="/api/v1")
    app.include_router(dashboard.router)
    return app


app = create_app()
