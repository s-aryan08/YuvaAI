"""
YuvaAI - Authentication Schemas

it defines request and response validation
for registration, login and user profiles.
"""

from datetime import datetime

from pydantic import (
    BaseModel,
    EmailStr,
    Field
)


# ==========================================
# 1. USER REGISTRATION
# ==========================================

class RegisterRequest(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=120
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128
    )


# ==========================================
# 2. USER LOGIN
# ==========================================

class LoginRequest(BaseModel):

    email: EmailStr

    password: str = Field(
        min_length=1,
        max_length=128
    )


# ==========================================
# 3. PUBLIC USER RESPONSE
# ==========================================

class UserResponse(BaseModel):

    id: int

    name: str

    email: EmailStr

    is_verified: bool

    created_at: datetime


# ==========================================
# 4. AUTHENTICATION RESPONSE
# ==========================================

class AuthResponse(BaseModel):

    message: str

    user: UserResponse