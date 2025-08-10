from __future__ import annotations

import json
import os
from typing import Any, Optional

from redis.asyncio import Redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DEFAULT_TTL = int(os.getenv("CACHE_TTL_SECONDS", "3600"))  # 1 hora por padrão

_redis_singleton: Optional[Redis] = None


async def get_redis() -> Redis:
    """
    Retorna conexão Redis (singleton).
    """
    global _redis_singleton
    if _redis_singleton is None:
        _redis_singleton = Redis.from_url(REDIS_URL, decode_responses=True)
    return _redis_singleton


async def cache_get_json(key: str) -> Any | None:
    """
    Recupera valor JSON armazenado no Redis.
    Retorna None se a chave não existir ou valor inválido.
    """
    r = await get_redis()
    raw = await r.get(key)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


async def cache_set_json(key: str, value: Any, ttl: int = DEFAULT_TTL) -> None:
    """
    Serializa `value` em JSON e armazena no Redis com TTL (expiração em segundos).
    """
    r = await get_redis()
    await r.set(key, json.dumps(value), ex=ttl)


async def cache_delete(key: str) -> None:
    """
    Remove chave do Redis.
    """
    r = await get_redis()
    await r.delete(key)

async def cache_ttl(key: str) -> int | None:
    """
    Retorna o TTL (segundos) da chave, ou None se não existir ou não tiver expiração.
    """
    r = await get_redis()
    t = await r.ttl(key)
    return t if t >= 0 else None