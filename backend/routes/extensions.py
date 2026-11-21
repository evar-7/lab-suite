from fastapi import APIRouter


router = APIRouter()


@router.get("/api/v1/extensions")
async def get_extensions():
    return {
        "extensions": [
            {
                "id": "lab-suite",
                "name": "Lab Suite",
                "version": "1.0.0",
                "description": "Extension modular de herramientas de productividad",
                "status": "active",
            }
        ]
    }

