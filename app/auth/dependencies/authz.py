from fastapi import Depends, HTTPException, Request, status
from app.auth.dependencies.auth import get_current_user
from app.db.models import User

def admin_required(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    return user

def read_only(request: Request, user: User = Depends(get_current_user)) -> User:
    """
    Libera GET/HEAD/OPTIONS para usuário autenticado.
    Para POST/PUT/PATCH/DELETE, exige admin.
    """
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return user
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Read-only user")
    return user
