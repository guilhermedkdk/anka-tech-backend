from __future__ import annotations

"""CRUD de alocações por cliente."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, status, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.base import get_db
from app.db import models as m
from app.schemas.allocations import AllocationCreate, AllocationUpdate, AllocationOut
from app.auth.dependencies.authz import read_only, admin_required

router = APIRouter(prefix="/clients/{client_id}/allocations", tags=["allocations"])


async def _ensure_client_exists(db: AsyncSession, client_id: int) -> None:
    """404 se o cliente não existir."""
    res = await db.execute(select(m.Client.id).where(m.Client.id == client_id))
    if res.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Client not found")


async def _get_or_create_asset(db: AsyncSession, ticker: str) -> m.Asset:
    """Busca Asset por ticker; cria se não existir (normaliza UPPER)."""
    ticker_up = ticker.strip().upper()
    res = await db.execute(select(m.Asset).where(m.Asset.ticker == ticker_up))
    asset = res.scalar_one_or_none()
    if asset:
        return asset
    asset = m.Asset(ticker=ticker_up)
    db.add(asset)
    await db.flush()  # garante asset.id
    return asset


@router.get(
    "",
    response_model=List[AllocationOut],
    dependencies=[Depends(read_only)],
)
async def list_allocations(
    client_id: int = Path(..., ge=1, description="ID do cliente"),
    db: AsyncSession = Depends(get_db),
) -> List[AllocationOut]:
    """Lista alocações (sem cálculos)."""
    await _ensure_client_exists(db, client_id)

    # Eager-load do asset p/ evitar lazy-load em AsyncSession (MissingGreenlet)
    res = await db.execute(
        select(m.Allocation)
        .options(selectinload(m.Allocation.asset))
        .where(m.Allocation.client_id == client_id)
        .order_by(m.Allocation.id.desc())
    )
    rows = list(res.scalars().all())

    return [
        AllocationOut(
            id=row.id,
            client_id=row.client_id,
            ticker=row.asset.ticker,
            quantity=row.quantity,
            buy_price=row.buy_price,
            buy_date=row.buy_date,
        )
        for row in rows
    ]


@router.post(
    "",
    response_model=AllocationOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(admin_required)],
)
async def create_allocation(
    client_id: int,
    payload: AllocationCreate,
    db: AsyncSession = Depends(get_db),
) -> AllocationOut:
    """Cria alocação; upsert de Asset por ticker."""
    await _ensure_client_exists(db, client_id)
    asset = await _get_or_create_asset(db, payload.ticker)

    row = m.Allocation(
        client_id=client_id,
        asset_id=asset.id,
        quantity=payload.quantity,
        buy_price=payload.buy_price,
        buy_date=payload.buy_date,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)

    return AllocationOut(
        id=row.id,
        client_id=row.client_id,
        ticker=asset.ticker,  # já resolvido
        quantity=row.quantity,
        buy_price=row.buy_price,
        buy_date=row.buy_date,
    )


@router.patch(
    "/{allocation_id}",
    response_model=AllocationOut,
    dependencies=[Depends(admin_required)],
)
async def update_allocation(
    client_id: int,
    allocation_id: int,
    payload: AllocationUpdate,
    db: AsyncSession = Depends(get_db),
) -> AllocationOut:
    """Atualiza parcialmente quantity/buy_price/buy_date (não troca ticker)."""
    await _ensure_client_exists(db, client_id)

    res = await db.execute(
        select(m.Allocation)
        .options(selectinload(m.Allocation.asset))
        .where(
            m.Allocation.id == allocation_id,
            m.Allocation.client_id == client_id,
        )
    )
    row = res.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Allocation not found")

    if payload.quantity is not None:
        row.quantity = payload.quantity
    if payload.buy_price is not None:
        row.buy_price = payload.buy_price
    if payload.buy_date is not None:
        row.buy_date = payload.buy_date

    ticker = row.asset.ticker  # lê antes do commit

    await db.commit()
    await db.refresh(row)

    return AllocationOut(
        id=row.id,
        client_id=row.client_id,
        ticker=ticker,
        quantity=row.quantity,
        buy_price=row.buy_price,
        buy_date=row.buy_date,
    )


@router.delete(
    "/{allocation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,  # 204 sem body
    dependencies=[Depends(admin_required)],
)
async def delete_allocation(
    client_id: int,
    allocation_id: int,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Remove alocação do cliente."""
    await _ensure_client_exists(db, client_id)

    res = await db.execute(
        select(m.Allocation).where(
            m.Allocation.id == allocation_id,
            m.Allocation.client_id == client_id,
        )
    )
    row = res.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Allocation not found")

    await db.delete(row)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
