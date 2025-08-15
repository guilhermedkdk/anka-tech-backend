from __future__ import annotations
import os, asyncio
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.db import models as m

# hash de senha (usa passlib)
from passlib.context import CryptContext
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

DATABASE_URL = os.getenv("DATABASE_URL")

# ✅ agora com domínio example.com
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
SEED_DEMO = os.getenv("SEED_DEMO", "1") not in ("0", "false", "False", "")

async def _get_or_create_asset(db: AsyncSession, ticker: str) -> m.Asset:
    t = ticker.strip().upper()
    r = await db.execute(select(m.Asset).where(m.Asset.ticker == t))
    asset = r.scalar_one_or_none()
    if asset:
        return asset
    asset = m.Asset(ticker=t)
    db.add(asset)
    await db.flush()
    return asset

async def _ensure_admin(db: AsyncSession) -> None:
    r = await db.execute(select(m.User).where(m.User.email == ADMIN_EMAIL))
    user = r.scalar_one_or_none()
    if user:
        user.is_admin = True
        user.is_active = True
        return
    db.add(m.User(
        email=ADMIN_EMAIL,
        hashed_password=pwd.hash(ADMIN_PASSWORD),
        is_active=True,
        is_admin=True,
    ))

async def _seed_demo_data(db: AsyncSession) -> None:
    # ✅ já em example.com
    clients = [
        ("Alice Invest", "alice@example.com"),
        ("Bob Capital",  "bob@example.com"),
    ]
    created_ids = []
    for name, email in clients:
        r = await db.execute(select(m.Client).where(m.Client.email == email))
        c = r.scalar_one_or_none()
        if not c:
            c = m.Client(name=name, email=email, status=m.ClientStatus.active)
            db.add(c)
            await db.flush()
        created_ids.append(c.id)

    demo_allocs = [
        (created_ids[0], "VALE3.SA", "100.00000000", "60.50000000", date(2024, 10, 21)),
        (created_ids[0], "PETR4.SA", "50.00000000",  "38.20000000", date(2024, 11,  5)),
        (created_ids[1], "ITUB4.SA", "80.00000000",  "29.90000000", date(2025,  1, 15)),
    ]

    for client_id, ticker, qty, price, buy_date in demo_allocs:
        r = await db.execute(
            select(m.Allocation)
            .join(m.Asset)
            .where(m.Allocation.client_id == client_id, m.Asset.ticker == ticker.upper())
        )
        if r.scalar_one_or_none():
            continue
        asset = await _get_or_create_asset(db, ticker)
        db.add(m.Allocation(
            client_id=client_id,
            asset_id=asset.id,
            quantity=qty,
            buy_price=price,
            buy_date=buy_date,
        ))

async def main() -> None:
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL não definido")
    engine = create_async_engine(DATABASE_URL, echo=False)
    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with Session() as db:
        await _ensure_admin(db)
        if SEED_DEMO:
            await _seed_demo_data(db)
        await db.commit()
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
