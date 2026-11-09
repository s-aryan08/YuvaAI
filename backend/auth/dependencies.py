"""
YuvaAI - Authentication Dependencies

Verifies authenticated users using JWT cookies.
"""

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User
from backend.auth.security import decode_access_token


# ==========================================
# 1. COOKIE CONFIGURATION
# ==========================================

ACCESS_COOKIE_NAME = "yuvaai_access_token"


# ==========================================
# 2. GET CURRENT USER
# ==========================================

def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:

    token = request.cookies.get(ACCESS_COOKIE_NAME)

    if not token:

        raise HTTPException(
            status_code=401,
            detail="Authentication required."
        )

    user_id = decode_access_token(token)

    if user_id is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session."
        )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None or not user.is_active:

        raise HTTPException(
            status_code=401,
            detail="User account is unavailable."
        )

    return user