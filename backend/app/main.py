from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.session import engine

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(settings.debug)
    if settings.auto_create_tables:
        from app.db import models  # noqa: F401
        from app.db.base import Base

        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.routes import agents, chat, conversations, documents, health, me  # noqa: E402

app.include_router(health.router, prefix="/api")
for api_router in (documents.router, chat.router, agents.router, conversations.router, me.router):
    app.include_router(api_router, prefix=settings.api_prefix)
