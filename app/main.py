from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.base import get_db

def create_app() -> FastAPI:
    app = FastAPI(title="invest-backend")

    @app.get("/")
    async def root(db: AsyncSession = Depends(get_db)):
        await db.execute(text("SELECT 1"))
        return {"message": "hello from FastAPI with Postgres"}

    return app

app = create_app()
