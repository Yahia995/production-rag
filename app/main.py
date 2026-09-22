import logging

from fastapi import FastAPI

from app.api.routes.chat import router as chat_router
from app.api.routes.documents import router as documents_router
from app.api.routes.health import router as health_router
from app.core.config import get_settings
from app.core.logging import configure_logging

configure_logging()

settings = get_settings()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Production RAG Platform",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(chat_router)
app.include_router(documents_router)


@app.on_event("startup")
async def startup() -> None:
    logger.info("application started")


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "environment": settings.app_env,
    }
