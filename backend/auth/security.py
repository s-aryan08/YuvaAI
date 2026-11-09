"""
YuvaAI - Authentication Security

Provides:
- Argon2 password hashing
- Password verification
- JWT access-token generation
- JWT access-token verification
"""

from datetime import datetime, timedelta, timezone

import jwt

from pwdlib import PasswordHash
from jwt.exceptions import InvalidTokenError

from backend.config import (
    AUTH_SECRET_KEY,
    AUTH_TOKEN_EXPIRE_MINUTES
)


# ==========================================
# 1. SECURITY CONFIGURATION
# ==========================================

if not AUTH_SECRET_KEY:
    raise RuntimeError(
        "AUTH_SECRET_KEY is missing from .env"
    )

password_hasher = PasswordHash.recommended()

JWT_ALGORITHM = "HS256"

JWT_ISSUER = "YuvaAI"

JWT_AUDIENCE = "YuvaAI-Web"


# ==========================================
# 2. PASSWORD HASHING
# ==========================================

def hash_password(password: str) -> str:

    if not isinstance(password, str):
        raise ValueError("Password must be a string.")

    if len(password) < 8:
        raise ValueError(
            "Password must contain at least 8 characters."
        )

    if len(password) > 128:
        raise ValueError(
            "Password cannot exceed 128 characters."
        )

    return password_hasher.hash(password)


# ==========================================
# 3. PASSWORD VERIFICATION
# ==========================================

def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    if not isinstance(plain_password, str):
        return False

    if not isinstance(hashed_password, str):
        return False

    try:

        return password_hasher.verify(
            plain_password,
            hashed_password
        )

    except Exception:

        return False


# ==========================================
# 4. CREATE ACCESS TOKEN
# ==========================================

def create_access_token(user_id: int) -> str:

    if not isinstance(user_id, int) or user_id <= 0:
        raise ValueError("Invalid user ID.")

    now = datetime.now(timezone.utc)

    expiration = now + timedelta(
        minutes=AUTH_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": now,
        "exp": expiration,
        "type": "access"
    }

    token = jwt.encode(
        payload,
        AUTH_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )

    return token


# ==========================================
# 5. VERIFY ACCESS TOKEN
# ==========================================

def decode_access_token(token: str):

    if not token:
        return None

    try:

        payload = jwt.decode(
            token,
            AUTH_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            issuer=JWT_ISSUER,
            audience=JWT_AUDIENCE
        )

        if payload.get("type") != "access":
            return None

        subject = payload.get("sub")

        if not subject or not subject.isdigit():
            return None

        user_id = int(subject)

        if user_id <= 0:
            return None

        return user_id

    except (InvalidTokenError, ValueError, TypeError):

        return None