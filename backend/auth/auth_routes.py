"""
YuvaAI - Authentication API Routes

Endpoints: i've listed  Asap pov
- GET  /api/auth/csrf
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/logout
- GET  /api/auth/me
"""

import secrets

from hmac import compare_digest

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Header,
    Request,
    Response,
    status
)

from sqlalchemy.orm import Session

from backend.database import get_db
from backend.config import (
    DEBUG,
    AUTH_TOKEN_EXPIRE_MINUTES
)

from backend.auth.schemas import (
    RegisterRequest,
    LoginRequest
)

from backend.auth.security import (
    create_access_token
)

from backend.auth.dependencies import (
    get_current_user,
    ACCESS_COOKIE_NAME
)

from backend.auth.auth_service import (
    register_user,
    authenticate_user,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    AccountDisabledError
)


# ==========================================
# 1. ROUTER CONFIGURATION
# ==========================================

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


CSRF_COOKIE_NAME = "yuvaai_csrf"


# ==========================================
# 2. COOKIE CONFIGURATION
# ==========================================

def set_auth_cookie(
    response: Response,
    token: str
):

    response.set_cookie(
        key=ACCESS_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=not DEBUG,
        samesite="lax",
        max_age=AUTH_TOKEN_EXPIRE_MINUTES * 60,
        path="/"
    )


def set_csrf_cookie(
    response: Response,
    token: str
):

    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=token,
        httponly=False,
        secure=not DEBUG,
        samesite="lax",
        max_age=AUTH_TOKEN_EXPIRE_MINUTES * 60,
        path="/"
    )


def clear_auth_cookies(response: Response):

    response.delete_cookie(
        key=ACCESS_COOKIE_NAME,
        path="/",
        secure=not DEBUG,
        httponly=True,
        samesite="lax"
    )

    response.delete_cookie(
        key=CSRF_COOKIE_NAME,
        path="/",
        secure=not DEBUG,
        httponly=False,
        samesite="lax"
    )


# ==========================================
# 3. CSRF VALIDATION
# ==========================================

def require_csrf(
    request: Request,
    x_csrf_token: str | None = Header(
        default=None,
        alias="X-CSRF-Token"
    )
):

    cookie_token = request.cookies.get(
        CSRF_COOKIE_NAME
    )

    if (
        not cookie_token
        or not x_csrf_token
        or not compare_digest(
            cookie_token,
            x_csrf_token
        )
    ):

        raise HTTPException(
            status_code=403,
            detail="CSRF validation failed."
        )


# ==========================================
# 4. PUBLIC USER RESPONSE
# ==========================================

def serialize_user(user):

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "is_verified": user.is_verified,
        "created_at": user.created_at.isoformat()
    }


# ==========================================
# 5. GENERATE CSRF TOKEN
# ==========================================

@router.get("/csrf")
def get_csrf_token(response: Response):

    token = secrets.token_urlsafe(32)

    set_csrf_cookie(
        response,
        token
    )

    return {
        "csrf_token": token
    }


# ==========================================
# 6. REGISTER USER
# ==========================================

@router.post("/register")
def register(
    request: RegisterRequest,
    response: Response,
    db: Session = Depends(get_db),
    _: None = Depends(require_csrf)
):

    try:

        user = register_user(
            db=db,
            name=request.name,
            email=str(request.email),
            password=request.password
        )

        access_token = create_access_token(
            user.id
        )

        set_auth_cookie(
            response,
            access_token
        )

        # Account is created, but email
        # verification has not been implemented yet.

        return {
            "message": "Account created successfully.",
            "user": serialize_user(user),
            "verification_required": True
        }

    except EmailAlreadyRegisteredError as error:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


# ==========================================
# 7. LOGIN USER
# ==========================================

@router.post("/login")
def login(
    request: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
    _: None = Depends(require_csrf)
):

    try:

        user = authenticate_user(
            db=db,
            email=str(request.email),
            password=request.password
        )

        access_token = create_access_token(
            user.id
        )

        set_auth_cookie(
            response,
            access_token
        )

        return {
            "message": "Login successful.",
            "user": serialize_user(user)
        }

    except InvalidCredentialsError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )

    except AccountDisabledError as error:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error)
        )


# ==========================================
# 8. GET CURRENT USER
# ==========================================

@router.get("/me")
def get_me(
    user=Depends(get_current_user)
):

    return {
        "authenticated": True,
        "user": serialize_user(user)
    }


# ==========================================
# 9. LOGOUT USER
# ==========================================

@router.post("/logout")
def logout(
    response: Response,
    _: None = Depends(require_csrf)
):

    clear_auth_cookies(response)

    return {
        "message": "Logged out successfully."
    }