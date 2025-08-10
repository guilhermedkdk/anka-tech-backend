from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routers.clients import router as clients_router
from app.api.routers.auth import router as auth_router

def create_app() -> FastAPI:
    app = FastAPI(title="invest-backend")

    # CORS (permite o frontend acessar a API no navegador)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,  # ex.: ["http://localhost:3000"]
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # Rotas de domínio
    app.include_router(auth_router)    # /auth (login/refresh)
    app.include_router(clients_router) # /clients (CRUD)

    return app


app = create_app()
