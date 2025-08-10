from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError

from app.db.base import get_db
from app.schemas.auth import LoginIn, RefreshIn, TokenPair
from app.auth.hashing import verify_password
from app.auth.jwt import create_access_token, create_refresh_token, decode_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenPair)
async def login(payload: LoginIn, db: AsyncSession = Depends(get_db)):
    from app.db.models import User

    user = await db.scalar(select(User).where(User.email == payload.email))
    if not user or not user.is_active or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access = create_access_token(sub=user.email, scopes=["admin"] if user.is_admin else ["read"])
    refresh = create_refresh_token(sub=user.email)
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}

@router.post("/refresh", response_model=TokenPair)
async def refresh(body: RefreshIn):
    try:
        data = decode_token(body.token)
        if data.get("type") != "refresh":
            raise ValueError("not a refresh token")
        sub: str = data["sub"]
    except (JWTError, ValueError, KeyError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access = create_access_token(sub=sub)
    return {"access_token": access, "refresh_token": body.token, "token_type": "bearer"}
