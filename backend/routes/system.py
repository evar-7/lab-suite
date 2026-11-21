from fastapi import APIRouter

from config import get_settings


router = APIRouter()
settings = get_settings()


@router.get("/")
async def root():
    return {
        "message": f"{settings.api_title} - v{settings.api_version}",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "lab-suite-api",
    }

