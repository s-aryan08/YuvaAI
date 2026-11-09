"""
YuvaAI - Main FastAPI Application

Provides authenticated APIs for:
- Conversations
- AI chat
- Streaming chat
- Usage tracking
- Health monitoring
"""

import json
import os

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    status
)

from fastapi.responses import StreamingResponse

from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, Field

from sqlalchemy.orm import Session

from backend.config import (
    DEBUG,
    APP_NAME,
    APP_VERSION
)

from backend.database import get_db

from backend.models import Conversation, Message, User

from backend.chat_service import (
    create_conversation,
    get_all_conversations,
    get_conversation_history,
    get_owned_conversation,
    chat,
    stream_chat,
    delete_conversation
)

from backend.usage_service import (
    check_and_record_usage,
    UsageLimitExceeded
)

from backend.auth.auth_routes import (
    router as auth_router,
    require_csrf
)

from backend.auth.dependencies import (
    get_current_user
)

from pathlib import Path
from fastapi.staticfiles import StaticFiles


# ============================================================
# 1. INITIALIZE FASTAPI
# ============================================================

app = FastAPI(
    title=f"{APP_NAME} API",
    description=(
        "AI-powered conversational assistant "
        "using Groq and PostgreSQL."
    ),
    version=APP_VERSION,
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None,
    openapi_url="/openapi.json" if DEBUG else None
)


# ============================================================
# 2. CORS CONFIGURATION
# ============================================================

def get_allowed_origins():

    """
    Returns permitted frontend origins.

    Production:
        Configure CORS_ALLOWED_ORIGINS as a comma-separated
        list of trusted frontend URLs.

    Development:
        Localhost origins are permitted when DEBUG=True.
    """

    configured_origins = os.getenv(
        "CORS_ALLOWED_ORIGINS",
        ""
    ).strip()

    origins = [
        origin.strip().rstrip("/")
        for origin in configured_origins.split(",")
        if origin.strip()
    ]

    if DEBUG:

        development_origins = [
            "http://localhost:5500",
            "http://127.0.0.1:5500",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "http://localhost:63342",
            "http://127.0.0.1:63342"
        ]

        origins.extend(development_origins)

    # Remove duplicates while preserving order.

    origins = list(dict.fromkeys(origins))

    if "*" in origins:

        raise ValueError(
            "Wildcard CORS origins cannot be used "
            "with credentialed requests."
        )

    return origins


allowed_origins = get_allowed_origins()


app.add_middleware(
    CORSMiddleware,

    allow_origins=allowed_origins,

    allow_credentials=True,

    allow_methods=[
        "GET",
        "POST",
        "PATCH",
        "PUT",
        "DELETE",
        "OPTIONS"
    ],

    allow_headers=[
        "Content-Type",
        "Authorization",
        "X-CSRF-Token",
        "Accept"
    ],

    expose_headers=[
        "Content-Type"
    ]
)


# ============================================================
# 3. AUTHENTICATION ROUTES
# ============================================================

app.include_router(auth_router)


# ============================================================
# 4. REQUEST SCHEMAS
# ============================================================

class ConversationCreate(BaseModel):

    title: str = Field(
        default="New Chat",
        min_length=1,
        max_length=255
    )


class ChatRequest(BaseModel):

    message: str = Field(
        min_length=1,
        max_length=4000
    )

    conversation_id: int | None = Field(
        default=None,
        gt=0
    )


# ============================================================
# 5. SERIALIZATION HELPERS
# ============================================================

def serialize_message(message: Message):

    return {
        "id": message.id,
        "role": message.role,
        "content": message.content,
        "created_at": message.created_at.isoformat()
    }


def serialize_conversation(conversation: Conversation):

    return {
        "id": conversation.id,
        "title": conversation.title,
        "model": conversation.model,
        "created_at": conversation.created_at.isoformat(),
        "updated_at": conversation.updated_at.isoformat()
    }


# ============================================================
# 6. HEALTH CHECK
# ============================================================

@app.get(
    "/health",
    tags=["Monitoring"]
)
def health_check():

    """
    Basic application health endpoint.

    Used by deployment platforms to verify that
    the FastAPI application is responding.
    """

    return {
        "status": "healthy",
        "application": APP_NAME,
        "version": APP_VERSION
    }


# ============================================================
# 7. CREATE CONVERSATION
# ============================================================

@app.post(
    "/api/conversations",
    tags=["Conversations"]
)
def create_new_conversation(

    request: ConversationCreate,

    user: User = Depends(get_current_user),

    _: None = Depends(require_csrf),

    db: Session = Depends(get_db)

):

    try:

        title = request.title.strip()

        if not title:

            raise HTTPException(
                status_code=400,
                detail="Conversation title cannot be empty."
            )

        conversation = create_conversation(
            db=db,
            title=title,
            user_id=user.id
        )

        return serialize_conversation(conversation)

    except HTTPException:

        raise

    except Exception as error:

        db.rollback()

        print(
            "[YuvaAI] Conversation creation error:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to create conversation."
        )


# ============================================================
# 8. GET USER CONVERSATIONS
# ============================================================

@app.get(
    "/api/conversations",
    tags=["Conversations"]
)
def list_conversations(

    user: User = Depends(get_current_user),

    db: Session = Depends(get_db)

):

    conversations = get_all_conversations(
        db,
        user.id
    )

    return [
        serialize_conversation(conversation)
        for conversation in conversations
    ]


# ============================================================
# 9. GET SINGLE CONVERSATION
# ============================================================

@app.get(
    "/api/conversations/{conversation_id}",
    tags=["Conversations"]
)
def get_single_conversation(

    conversation_id: int,

    user: User = Depends(get_current_user),

    db: Session = Depends(get_db)

):

    conversation = get_owned_conversation(
        db,
        conversation_id,
        user.id
    )

    if conversation is None:

        raise HTTPException(
            status_code=404,
            detail="Conversation not found."
        )

    messages = get_conversation_history(
        db,
        conversation_id
    )

    return {
        "conversation": serialize_conversation(conversation),
        "messages": messages
    }


# ============================================================
# 10. SEND NORMAL CHAT MESSAGE
# ============================================================

@app.post(
    "/api/chat",
    tags=["Chat"]
)
def send_chat_message(

    request: ChatRequest,

    user: User = Depends(get_current_user),

    _: None = Depends(require_csrf),

    db: Session = Depends(get_db)

):

    try:

        message = request.message.strip()

        if not message:

            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty."
            )

        # Verify conversation ownership before consuming quota.

        if request.conversation_id is not None:

            conversation = get_owned_conversation(
                db,
                request.conversation_id,
                user.id
            )

            if conversation is None:

                raise HTTPException(
                    status_code=404,
                    detail="Conversation not found."
                )

        # Record authenticated user usage.

        usage = check_and_record_usage(
            db,
            user.id
        )

        # Create a new user-owned conversation.

        if request.conversation_id is None:

            conversation = create_conversation(
                db,
                message[:50],
                user_id=user.id
            )

            conversation_id = conversation.id

        else:

            conversation_id = request.conversation_id

        result = chat(
            db,
            conversation_id,
            message,
            user_id=user.id
        )

        result["usage"] = usage

        return result

    except UsageLimitExceeded as error:

        raise HTTPException(
            status_code=429,
            detail={
                "message": error.message,
                "limit_type": error.limit_type
            }
        )

    except ValueError as error:

        db.rollback()

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except HTTPException:

        raise

    except Exception as error:

        db.rollback()

        print(
            "[YuvaAI] Chat API error:",
            error
        )

        raise HTTPException(
            status_code=502,
            detail="YuvaAI could not generate a response."
        )


# ============================================================
# 11. STREAMING CHAT MESSAGE
# ============================================================

@app.post(
    "/api/chat/stream",
    tags=["Chat"]
)
def send_streaming_chat_message(

    request: ChatRequest,

    user: User = Depends(get_current_user),

    _: None = Depends(require_csrf),

    db: Session = Depends(get_db)

):

    try:

        message = request.message.strip()

        if not message:

            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty."
            )

        # Verify ownership before recording usage.

        if request.conversation_id is not None:

            conversation = get_owned_conversation(
                db,
                request.conversation_id,
                user.id
            )

            if conversation is None:

                raise HTTPException(
                    status_code=404,
                    detail="Conversation not found."
                )

        usage = check_and_record_usage(
            db,
            user.id
        )

        if request.conversation_id is None:

            conversation = create_conversation(
                db,
                message[:50],
                user_id=user.id
            )

            conversation_id = conversation.id

        else:

            conversation_id = request.conversation_id

        # Capture authenticated ID for the generator.

        authenticated_user_id = user.id

        def event_stream():

            try:

                for chunk in stream_chat(
                    db,
                    conversation_id,
                    message,
                    user_id=authenticated_user_id
                ):

                    event_data = json.dumps({
                        "content": chunk
                    })

                    yield (
                        f"event: token\n"
                        f"data: {event_data}\n\n"
                    )

                done_data = json.dumps({
                    "conversation_id": conversation_id,
                    "usage": usage
                })

                yield (
                    f"event: done\n"
                    f"data: {done_data}\n\n"
                )

            except Exception as stream_error:

                db.rollback()

                print(
                    "[YuvaAI] Streaming API error:",
                    stream_error
                )

                error_data = json.dumps({
                    "message": "Unable to generate AI response."
                })

                yield (
                    f"event: error\n"
                    f"data: {error_data}\n\n"
                )

        return StreamingResponse(
            event_stream(),

            media_type="text/event-stream",

            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )

    except UsageLimitExceeded as error:

        raise HTTPException(
            status_code=429,
            detail={
                "message": error.message,
                "limit_type": error.limit_type
            }
        )

    except HTTPException:

        raise

    except Exception as error:

        db.rollback()

        print(
            "[YuvaAI] Streaming endpoint error:",
            error
        )

        raise HTTPException(
            status_code=502,
            detail="Unable to start streaming response."
        )


# ============================================================
# 12. DELETE CONVERSATION
# ============================================================

@app.delete(
    "/api/conversations/{conversation_id}",
    tags=["Conversations"]
)
def remove_conversation(

    conversation_id: int,

    user: User = Depends(get_current_user),

    _: None = Depends(require_csrf),

    db: Session = Depends(get_db)

):

    deleted = delete_conversation(
        db,
        conversation_id,
        user.id
    )

    if not deleted:

        raise HTTPException(
            status_code=404,
            detail="Conversation not found."
        )

    return {
        "message": "Conversation deleted successfully.",
        "conversation_id": conversation_id
    }

# ============================================================
# SERVE YUVAAI FRONTEND
# ============================================================

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

app.mount(
    "/",
    StaticFiles(
        directory=str(FRONTEND_DIR),
        html=True
    ),
    name="frontend"
)