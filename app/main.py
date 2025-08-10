from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.base import get_db
from app.core.redis_client import get_redis

def create_app() -> FastAPI:
    app = FastAPI(title="invest-backend")

    @app.get("/")
    async def root():
        return {"message": "hello from FastAPI"}

    @app.get("/health", tags=["health"])
    async def health(db: AsyncSession = Depends(get_db)):
        try:
            await db.execute(text("SELECT 1"))
            db_ok = True
        except Exception:
            db_ok = False

        try:
            r = await get_redis()
            await r.ping()
            redis_ok = True
        except Exception:
            redis_ok = False

        return {
            "status": "ok" if (db_ok and redis_ok) else "degraded",
            "db": db_ok,
            "redis": redis_ok
        }

    return app

app = create_app()
