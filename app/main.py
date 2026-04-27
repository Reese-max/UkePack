"""FastAPI application entrypoint."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import get_settings

_TEMPLATES = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))
_PUBLIC_SAMPLES_DIR = Path(__file__).resolve().parent.parent / "samples" / "public_domain"


def _homepage_cards() -> list[dict[str, str]]:
    return [
        {
            "title": "建立練習包",
            "description": "先建立歌曲專案，再走分析、轉 Key、輸出 PDF 流程。",
            "href": "/new",
        },
        {
            "title": "匯入 MusicXML",
            "description": "直接看匯入 API 說明，立刻把 MusicXML 丟進專案。",
            "href": "/docs#/default/import_musicxml_api_projects__project_id__import_post",
        },
        {
            "title": "看範例",
            "description": "下載公版小星星 MusicXML，直接試整條 demo pipeline。",
            "href": "/samples/public_domain/twinkle.musicxml",
        },
        {
            "title": "老師專區",
            "description": "建立專案後，可在分析頁進入老師審稿模式，調整和弦、刷法與練習說明。",
            "href": "/new",
        },
    ]


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
    application.mount(
        "/samples/public_domain",
        StaticFiles(directory=str(_PUBLIC_SAMPLES_DIR)),
        name="public-samples",
    )

    @application.get("/", response_class=HTMLResponse)
    def home(request: Request) -> HTMLResponse:
        return _TEMPLATES.TemplateResponse(
            request=request,
            name="index.html",
            context={"cta_cards": _homepage_cards()},
        )

    @application.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    from app.api.pages import router as pages_router
    from app.api.projects import router as projects_router
    from app.api.review_pages import router as review_pages_router

    application.include_router(projects_router)
    application.include_router(pages_router)
    application.include_router(review_pages_router)

    return application


app = create_app()
