from __future__ import annotations
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.db.models import Client, ClientStatus
from app.schemas.client import ClientCreate, ClientUpdate, ClientRead
from app.db.base import get_db

router = APIRouter(prefix="/clients", tags=["clients"])


@router.post(
    "",
    response_model=ClientRead,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"description": "Email já cadastrado"}},
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
    response_model=List[ClientRead],
)
async def list_clients(
    session: AsyncSession = Depends(get_db),
) -> List[ClientRead]:
    # Paginação/busca/filtro entram no próximo commit
    result = await session.execute(select(Client).order_by(Client.id))
    return list(result.scalars().all())


@router.put(
    "/{client_id}",
    response_model=ClientRead,
    responses={
        404: {"description": "Cliente não encontrado"},
        409: {"description": "Email já cadastrado"},
    },
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
    responses={
        404: {"description": "Cliente não encontrado"},
        409: {"description": "Email já cadastrado"},
    },
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

    # Resposta vazia (sem body) para cumprir 204
    return Response(status_code=status.HTTP_204_NO_CONTENT)
