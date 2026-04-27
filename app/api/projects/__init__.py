"""Projects API router package."""

from fastapi import APIRouter

from .crud import router as crud_router
from .export import router as export_router
from .import_ import router as import_router
from .license import router as license_router

router = APIRouter()
router.include_router(crud_router)
router.include_router(import_router)
router.include_router(license_router)
router.include_router(export_router)

__all__ = ["router"]
