"""
YuvaAI - Chat Service

Manages user-owned conversations, messages
and normal or streaming AI responses.
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.models import Conversation, Message
from backend.ai_engine import generate_response, stream_response
from backend.config import GROQ_MODEL


# ==========================================
# 1. CREATE CONVERSATION
# ==========================================

def create_conversation(
    db: Session,
    title: str = "New Chat",
    user_id: int = None
):

    if user_id is None:
        raise ValueError("Authenticated user required.")

    conversation = Conversation(
        title=title,
        model=GROQ_MODEL,
        user_id=user_id
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


# ==========================================
# 2. GET OWNED CONVERSATION
# ==========================================

def get_owned_conversation(
    db: Session,
    conversation_id: int,
    user_id: int
):

    return (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        .first()
    )


# ==========================================
# 3. SAVE MESSAGE
# ==========================================

def save_message(
    db: Session,
    conversation_id: int,
    role: str,
    content: str
):

    if role not in ("user", "assistant"):
        raise ValueError("Invalid message role.")

    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content
    )

    db.add(message)

    # Update conversation timestamp.
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )

    if conversation:
        from datetime import datetime, timezone

        conversation.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(message)

    return message


# ==========================================
# 4. GET CONVERSATION HISTORY
# ==========================================

def get_conversation_history(
    db: Session,
    conversation_id: int
):

    messages = (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation_id
        )
        .order_by(desc(Message.id))
        .limit(10)
        .all()
    )

    messages.reverse()

    return [
        {
            "role": message.role,
            "content": message.content
        }
        for message in messages
    ]


# ==========================================
# 5. GENERATE NORMAL CHAT RESPONSE
# ==========================================

def chat(
    db: Session,
    conversation_id: int,
    user_message: str,
    user_id: int
):

    if not user_message or not user_message.strip():
        raise ValueError("Message cannot be empty.")

    conversation = get_owned_conversation(
        db,
        conversation_id,
        user_id
    )

    if conversation is None:
        raise ValueError("Conversation not found.")

    history = get_conversation_history(
        db,
        conversation_id
    )

    save_message(
        db,
        conversation_id,
        "user",
        user_message.strip()
    )

    ai_response = generate_response(
        user_message,
        history=history
    )

    save_message(
        db,
        conversation_id,
        "assistant",
        ai_response
    )

    return {
        "conversation_id": conversation_id,
        "user_message": user_message,
        "assistant_message": ai_response
    }


# ==========================================
# 6. STREAMING CHAT RESPONSE
# ==========================================

def stream_chat(
    db: Session,
    conversation_id: int,
    user_message: str,
    user_id: int
):

    if not user_message or not user_message.strip():
        raise ValueError("Message cannot be empty.")

    conversation = get_owned_conversation(
        db,
        conversation_id,
        user_id
    )

    if conversation is None:
        raise ValueError("Conversation not found.")

    history = get_conversation_history(
        db,
        conversation_id
    )

    save_message(
        db,
        conversation_id,
        "user",
        user_message.strip()
    )

    generated_response = ""

    for chunk in stream_response(
        user_message,
        history=history
    ):

        generated_response += chunk

        yield chunk

    if generated_response.strip():

        save_message(
            db,
            conversation_id,
            "assistant",
            generated_response.strip()
        )

    print(
        f"[YuvaAI] Streaming response saved. "
        f"Conversation ID: {conversation_id}"
    )


# ==========================================
# 7. GET USER CONVERSATIONS
# ==========================================

def get_all_conversations(
    db: Session,
    user_id: int
):

    return (
        db.query(Conversation)
        .filter(
            Conversation.user_id == user_id
        )
        .order_by(desc(Conversation.updated_at))
        .all()
    )


# ==========================================
# 8. DELETE USER CONVERSATION
# ==========================================

def delete_conversation(
    db: Session,
    conversation_id: int,
    user_id: int
):

    conversation = get_owned_conversation(
        db,
        conversation_id,
        user_id
    )

    if conversation is None:
        return False

    db.delete(conversation)
    db.commit()

    return True