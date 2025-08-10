from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from jose import jwt

SECRET_KEY: str = os.getenv("SECRET_KEY", "secret")
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", "43200"))  # 30 dias

def _encode(payload: Dict[str, Any], minutes: int) -> str:
    # Cria um JWT com 'iat' e 'exp' (timezone-aware)
    now = datetime.now(timezone.utc)
    to_encode = {**payload, "iat": now, "exp": now + timedelta(minutes=minutes)}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)

def create_access_token(sub: str, scopes: Optional[List[str]] = None) -> str:
    # Gera um access token curto (expira em ACCESS_TOKEN_EXPIRE_MINUTES)
    return _encode({"sub": sub, "scopes": scopes or ["read"]}, ACCESS_TOKEN_EXPIRE_MINUTES)

def create_refresh_token(sub: str) -> str:
    # Gera um refresh token longo (expira em REFRESH_TOKEN_EXPIRE_MINUTES)
    return _encode({"sub": sub, "type": "refresh"}, REFRESH_TOKEN_EXPIRE_MINUTES)

def decode_token(token: str) -> Dict[str, Any]:
    # Decodifica e valida assinatura/expiração do JWT
    return jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
