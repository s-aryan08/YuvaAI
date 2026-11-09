"""
YuvaAI - Database Models

Defines users, conversations, messages
and application usage records.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text
)

from sqlalchemy.orm import relationship

from backend.database import Base


# ==========================================
# 1. USER MODEL
# ==========================================

class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True
    )

    name = Column(
        String(120),
        nullable=False
    )

    email = Column(
        String(254),
        nullable=False,
        unique=True,
        index=True
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    is_verified = Column(
        Boolean,
        default=False,
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # One user can own multiple conversations.

    conversations = relationship(
        "Conversation",
        back_populates="user"
    )


# ==========================================
# 2. CONVERSATION MODEL
# ==========================================

class Conversation(Base):

    __tablename__ = "conversations"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # Nullable to preserve existing anonymous chats.

    user_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
            name="fk_conversations_user_id_users"
        ),
        nullable=True,
        index=True
    )

    title = Column(
        String(255),
        nullable=False
    )

    model = Column(
        String(100),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Each conversation belongs to one user.

    user = relationship(
        "User",
        back_populates="conversations"
    )

    # One conversation can contain multiple messages.

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan"
    )


# ==========================================
# 3. MESSAGE MODEL
# ==========================================

class Message(Base):

    __tablename__ = "messages"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    conversation_id = Column(
        Integer,
        ForeignKey(
            "conversations.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    role = Column(
        String(20),
        nullable=False
    )

    content = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Each message belongs to one conversation.

    conversation = relationship(
        "Conversation",
        back_populates="messages"
    )


# ==========================================
# 4. USAGE RECORD MODEL
# ==========================================

class UsageRecord(Base):

    __tablename__ = "usage_records"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    client_id = Column(
        String,
        nullable=False,
        index=True
    )



    usage_date = Column(
        Date,
        default=lambda: datetime.now(timezone.utc).date()
    )

    message_count = Column(
        Integer,
        default=0
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )


# ==========================================
# 5. USAGE EVENT MODEL
# ==========================================

class UsageEvent(Base):

    __tablename__ = "usage_events"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    client_id = Column(
        String,
        nullable=False,
        index=True
    )



    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        Index(
            "idx_usage_client_created",
            "client_id",
            "created_at"
        ),
    )