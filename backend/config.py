"""
YuvaAI - Configuration Module

Purpose:
Manages application settings, environment variables,
AI provider configuration, database settings and authentication.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


# ============================================================
# 1. PROJECT DIRECTORY
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)


# ============================================================
# 2. APPLICATION SETTINGS
# ============================================================

APP_NAME = "YuvaAI"

APP_VERSION = "1.0.0"

# Local development: DEBUG=True
# Production deployment: DEBUG=False

DEBUG = os.getenv("DEBUG", "False").strip().lower() == "true"


# ============================================================
# 3. AI PROVIDER CONFIGURATION
# ============================================================

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY", ""
).strip()

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
).strip()


# ============================================================
# 4. DATABASE CONFIGURATION
# ============================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL", ""
).strip()


# ============================================================
# 5. AUTHENTICATION CONFIGURATION
# ============================================================

AUTH_SECRET_KEY = os.getenv(
    "AUTH_SECRET_KEY", ""
).strip()


try:

    AUTH_TOKEN_EXPIRE_MINUTES = int(
        os.getenv(
            "AUTH_TOKEN_EXPIRE_MINUTES",
            "30"
        )
    )

except ValueError as error:

    raise ValueError(
        "AUTH_TOKEN_EXPIRE_MINUTES must be a valid integer."
    ) from error


if AUTH_TOKEN_EXPIRE_MINUTES <= 0:

    raise ValueError(
        "AUTH_TOKEN_EXPIRE_MINUTES must be positive."
    )


# ============================================================
# 6. CONFIGURATION VALIDATION
# ============================================================

def validate_settings():

    # Validate Groq API key.

    if not GROQ_API_KEY:

        raise ValueError(
            "GROQ_API_KEY is missing. "
            "Configure it in your environment variables."
        )


    # Validate AI model.

    if not GROQ_MODEL:

        raise ValueError(
            "GROQ_MODEL is not configured."
        )


    # Validate database.

    if not DATABASE_URL:

        raise ValueError(
            "DATABASE_URL is missing. "
            "Configure your PostgreSQL connection string."
        )


    # Validate authentication secret.

    if not AUTH_SECRET_KEY:

        raise ValueError(
            "AUTH_SECRET_KEY is missing. "
            "Configure a secure authentication secret."
        )


    if len(AUTH_SECRET_KEY) < 32:

        raise ValueError(
            "AUTH_SECRET_KEY must contain at least 32 characters."
        )


    # Prevent insecure default secrets in production.

    if not DEBUG:

        insecure_values = {
            "secret",
            "changeme",
            "your_secret_key",
            "your_secure_secret_key",
            "development"
        }

        if AUTH_SECRET_KEY.lower() in insecure_values:

            raise ValueError(
                "A secure AUTH_SECRET_KEY is required in production."
            )


    return True


# ============================================================
# 7. EXPORT CONFIGURATION
# ============================================================

__all__ = [
    "PROJECT_ROOT",
    "ENV_FILE",
    "APP_NAME",
    "APP_VERSION",
    "DEBUG",
    "GROQ_API_KEY",
    "GROQ_MODEL",
    "DATABASE_URL",
    "AUTH_SECRET_KEY",
    "AUTH_TOKEN_EXPIRE_MINUTES",
    "validate_settings"
]