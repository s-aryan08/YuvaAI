"""
YuvaAI - Authentication Service

Handles:
- User registration
- Email uniqueness
- Password hashing
- User authentication
- Account status validation
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.models import User

from backend.auth.security import (
    hash_password,
    verify_password
)


# ==========================================
# 1. AUTHENTICATION EXCEPTIONS
# ==========================================

class EmailAlreadyRegisteredError(Exception):
    """Raised when an email is already registered."""
    pass


class InvalidCredentialsError(Exception):
    """Raised when login credentials are invalid."""
    pass


class AccountDisabledError(Exception):
    """Raised when an account is disabled."""
    pass


# ==========================================
# 2. EMAIL NORMALIZATION
# ==========================================

def normalize_email(email: str) -> str:

    if not email:
        raise ValueError("Email cannot be empty.")

    return email.strip().lower()


# ==========================================
# 3. REGISTER USER
# ==========================================

def register_user(
    db: Session,
    name: str,
    email: str,
    password: str
) -> User:

    normalized_name = name.strip()
    normalized_email = normalize_email(email)

    if len(normalized_name) < 2:
        raise ValueError(
            "Name must contain at least 2 characters."
        )

    if len(normalized_name) > 120:
        raise ValueError(
            "Name cannot exceed 120 characters."
        )

    # Check whether the email already exists.

    existing_user = (
        db.query(User)
        .filter(User.email == normalized_email)
        .first()
    )

    if existing_user:
        raise EmailAlreadyRegisteredError(
            "An account with this email already exists."
        )

    # Hash the password using Argon2id.

    password_hash = hash_password(password)

    user = User(
        name=normalized_name,
        email=normalized_email,
        password_hash=password_hash,
        is_verified=False,
        is_active=True
    )

    try:

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    except IntegrityError:

        db.rollback()

        # Handles simultaneous registration attempts
        # for the same email.

        raise EmailAlreadyRegisteredError(
            "An account with this email already exists."
        )

    except Exception:

        db.rollback()
        raise


# ==========================================
# 4. AUTHENTICATE USER
# ==========================================

def authenticate_user(
    db: Session,
    email: str,
    password: str
) -> User:

    normalized_email = normalize_email(email)

    user = (
        db.query(User)
        .filter(User.email == normalized_email)
        .first()
    )

    # Return the same error for an unknown email
    # and an incorrect password.

    if user is None:

        raise InvalidCredentialsError(
            "Incorrect email or password."
        )

    if not verify_password(
        password,
        user.password_hash
    ):

        raise InvalidCredentialsError(
            "Incorrect email or password."
        )

    if not user.is_active:

        raise AccountDisabledError(
            "This account has been disabled."
        )

    return user


# ==========================================
# 5. GET USER BY ID
# ==========================================

def get_user_by_id(
    db: Session,
    user_id: int
):

    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )