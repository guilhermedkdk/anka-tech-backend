from __future__ import annotations

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routers.clients import router as clients_router
from app.api.routers.auth import router as auth_router
from app.api.routers.assets import router as assets_router

from app.integrations.yahoo import close_yahoo_client, get_yahoo
from app.cache.redis_cache import get_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: aquece dependências
    await get_yahoo()
    await get_redis()
    yield
    # Shutdown: libera recursos
    await close_yahoo_client()
    redis_conn = await get_redis()
    await redis_conn.close()


def create_app() -> FastAPI:
    app = FastAPI(title="invest-backend", lifespan=lifespan)

    # CORS p/ frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # Rotas
    app.include_router(auth_router)     # /auth
    app.include_router(clients_router)  # /clients
    app.include_router(assets_router)   # /assets/available

    return app


app = create_app()
