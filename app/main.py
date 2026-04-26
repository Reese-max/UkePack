"""FastAPI application entrypoint."""

from fastapi import FastAPI

from app.config import get_settings


def create_app() -> FastAPI:
    """Build the FastAPI application instance."""
    settings = get_settings()
    application = FastAPI(title="UkePack AI", debug=settings.debug)

    @application.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return application


app = create_app()
