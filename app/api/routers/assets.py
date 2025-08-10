from __future__ import annotations

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, Query, Response

from app.integrations.yahoo import get_yahoo
from app.cache.redis_cache import cache_get_json, cache_set_json, cache_ttl
from app.schemas.assets import AssetSearchItem

from app.auth.dependencies.authz import read_only

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get(
    "/available",
    response_model=List[AssetSearchItem],
    dependencies=[Depends(read_only)],
)
async def list_available_assets(
    q: str = Query(..., min_length=1, description="Termo de busca (ticker ou nome parcial)"),
    limit: int = Query(10, ge=1, le=50, description="Limite de resultados (máx. 50)"),
    yahoo = Depends(get_yahoo),
    response: Response = None,
) -> List[Dict[str, Any]]:
    """
    Lista dinâmica de ativos vinda da busca do Yahoo Finance, com cache em Redis (TTL 1h).

    Fluxo:
      1) Tenta no Redis (chave 'assets:search:{q}').
      2) Se não houver, consulta Yahoo, salva no Redis e retorna.
    """
    key = f"assets:search:{q.strip().lower()}"

    # 1) Tenta cache
    cached = await cache_get_json(key)
    if cached:
        if response is not None:
            response.headers["X-Cache"] = "HIT"
            ttl = await cache_ttl(key)
            if ttl is not None:
                response.headers["X-Cache-TTL"] = str(ttl)
            response.headers["X-Cache-Key"] = key
        return cached[:limit]

    # 2) Consulta Yahoo (sem try/except extra)
    results = await yahoo.search(query=q, quotes_count=limit)

    # 3) Salva no cache e devolve
    await cache_set_json(key, results)
    if response is not None:
        response.headers["X-Cache"] = "MISS"
        ttl = await cache_ttl(key)
        if ttl is not None:
            response.headers["X-Cache-TTL"] = str(ttl)
        response.headers["X-Cache-Key"] = key

    return results[:limit]
