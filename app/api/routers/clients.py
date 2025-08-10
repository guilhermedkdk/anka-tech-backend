from __future__ import annotations
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.db.models import Client, ClientStatus
from app.schemas.client import ClientCreate, ClientUpdate, ClientRead
from app.schemas.pagination import Page, PageMeta
from app.db.base import get_db
from app.auth.dependencies.authz import read_only, admin_required

router = APIRouter(
    prefix="/clients",
    tags=["clients"],
    dependencies=[Depends(read_only)],
)

MAX_PAGE_SIZE = 100


@router.post(
    "",
    response_model=ClientRead,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"description": "Email já cadastrado"}},
    dependencies=[Depends(admin_required)],
)
async def create_client(
    payload: ClientCreate,
    session: AsyncSession = Depends(get_db),
) -> ClientRead:
    client = Client(
        name=payload.name,
        email=payload.email,
        status=payload.status or ClientStatus.active,
    )
    session.add(client)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Email já cadastrado")
    await session.refresh(client)
    return client


@router.get(
    "/{client_id}",
    response_model=ClientRead,
    responses={404: {"description": "Cliente não encontrado"}},
)
async def get_client(
    client_id: int,
    session: AsyncSession = Depends(get_db),
) -> ClientRead:
    client = await session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return client


@router.get(
    "",
    response_model=Page[ClientRead],
)
async def list_clients(
    q: Optional[str] = Query(None, description="Busca por nome ou email (case-insensitive)"),
    status_filter: Optional[ClientStatus] = Query(None, alias="status", description="Filtro por status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=MAX_PAGE_SIZE),
    session: AsyncSession = Depends(get_db),
) -> Page[ClientRead]:
    stmt = select(Client)

    conditions = []
    if q:
        like = f"%{q}%"
        conditions.append(or_(Client.name.ilike(like), Client.email.ilike(like)))
    if status_filter is not None:
        conditions.append(Client.status == status_filter)
    if conditions:
        from sqlalchemy import and_
        stmt = stmt.where(and_(*conditions))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await session.execute(count_stmt)).scalar_one()

    stmt = stmt.order_by(Client.id).offset((page - 1) * page_size).limit(page_size)
    result = await session.execute(stmt)
    items = list(result.scalars().all())

    pages = (total + page_size - 1) // page_size if total else 0

    return Page[ClientRead](
        items=items,
        meta=PageMeta(total=total, page=page, page_size=page_size, pages=pages),
    )


@router.put(
    "/{client_id}",
    response_model=ClientRead,
    responses={404: {"description": "Cliente não encontrado"}, 409: {"description": "Email já cadastrado"}},
    dependencies=[Depends(admin_required)],
)
async def update_client_put(
    client_id: int,
    payload: ClientCreate,  # PUT substitui todos os campos do recurso
    session: AsyncSession = Depends(get_db),
) -> ClientRead:
    client = await session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    client.name = payload.name
    client.email = payload.email
    client.status = payload.status or ClientStatus.active

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Email já cadastrado")

    await session.refresh(client)
    return client


@router.patch(
    "/{client_id}",
    response_model=ClientRead,
    responses={404: {"description": "Cliente não encontrado"}, 409: {"description": "Email já cadastrado"}},
    dependencies=[Depends(admin_required)],
)
async def update_client_patch(
    client_id: int,
    payload: ClientUpdate,
    session: AsyncSession = Depends(get_db),
) -> ClientRead:
    client = await session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    if payload.name is not None:
        client.name = payload.name
    if payload.email is not None:
        client.email = payload.email
    if payload.status is not None:
        client.status = payload.status

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Email já cadastrado")

    await session.refresh(client)
    return client


@router.delete(
    "/{client_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Cliente não encontrado"}},
    dependencies=[Depends(admin_required)],
)
async def delete_client(
    client_id: int,
    session: AsyncSession = Depends(get_db),
) -> Response:
    client = await session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    await session.delete(client)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
