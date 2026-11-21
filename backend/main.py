from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from database import ensure_schema
from routes.darkmode import router as darkmode_router
from routes.extensions import router as extensions_router
from routes.feedback import router as feedback_router
from routes.system import router as system_router


settings = get_settings()


@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    ensure_schema()
    yield


app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(system_router)
app.include_router(extensions_router)
app.include_router(darkmode_router)
app.include_router(feedback_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)