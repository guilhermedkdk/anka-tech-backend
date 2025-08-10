# app/main.py
from __future__ import annotations

from fastapi import FastAPI
from app.api.clients import router as clients_router


def create_app() -> FastAPI:
    app = FastAPI(title="invest-backend")

    # Rotas de domínio
    app.include_router(clients_router)  # /clients (CRUD)

    return app


app = create_app()
