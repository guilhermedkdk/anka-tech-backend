from __future__ import annotations
import asyncio

from sqlalchemy import select
from app.core.config import settings
from app.db.base import get_db
from app.db.models import User
from app.auth.hashing import get_password_hash


async def seed_admin():
    if not settings.ADMIN_EMAIL or not settings.ADMIN_PASSWORD:
        print("[seed_admin] ADMIN_EMAIL e ADMIN_PASSWORD devem estar configurados no .env")
        return

    async for session in get_db():
        # Verifica se já existe
        existing = await session.scalar(select(User).where(User.email == settings.ADMIN_EMAIL))
        if existing:
            print(f"[seed_admin] Usuário admin '{settings.ADMIN_EMAIL}' já existe.")
            return

        # Cria novo admin
        admin = User(
            email=settings.ADMIN_EMAIL,
            hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
            is_active=True,
            is_admin=True,
        )
        session.add(admin)
        await session.commit()
        print(f"[seed_admin] Usuário admin '{settings.ADMIN_EMAIL}' criado com sucesso.")
        return


if __name__ == "__main__":
    asyncio.run(seed_admin())
