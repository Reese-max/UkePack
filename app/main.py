"""FastAPI application entrypoint."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings


@asynccontextmanager
async def _lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    from app.core.db import create_tables

    create_tables()
    yield


def create_app() -> FastAPI:
    """Build the FastAPI application instance."""
    settings = get_settings()
    application = FastAPI(
        title="UkePack AI", debug=settings.debug, lifespan=_lifespan
    )

    @application.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    from app.api.projects import router as projects_router

    application.include_router(projects_router)

    return application


app = create_app()
