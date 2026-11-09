"""
Add users and conversation ownership.

Revision ID: 97417ae7ebb7
Revises: f8d59f6fd0d1
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# ==========================================
# REVISION IDENTIFIERS
# ==========================================

revision: str = "97417ae7ebb7"

down_revision: Union[str, Sequence[str], None] = "f8d59f6fd0d1"

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None


# ==========================================
# UPGRADE
# ==========================================

def upgrade() -> None:

    # 1. Create users table.

    op.create_table(
        "users",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "name",
            sa.String(length=120),
            nullable=False
        ),

        sa.Column(
            "email",
            sa.String(length=254),
            nullable=False
        ),

        sa.Column(
            "password_hash",
            sa.String(length=255),
            nullable=False
        ),

        sa.Column(
            "is_verified",
            sa.Boolean(),
            nullable=False
        ),

        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False
        ),

        sa.PrimaryKeyConstraint("id")
    )

    # 2. Unique email index.

    op.create_index(
        "ix_users_email",
        "users",
        ["email"],
        unique=True
    )

    # 3. Add nullable user_id to existing conversations.

    op.add_column(
        "conversations",
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=True
        )
    )

    # 4. Add ownership index.

    op.create_index(
        "ix_conversations_user_id",
        "conversations",
        ["user_id"],
        unique=False
    )

    # 5. Add named foreign key.

    op.create_foreign_key(
        "fk_conversations_user_id_users",

        "conversations",

        "users",

        ["user_id"],

        ["id"],

        ondelete="SET NULL"
    )


# ==========================================
# DOWNGRADE
# ==========================================

def downgrade() -> None:

    # Remove foreign key first.

    op.drop_constraint(
        "fk_conversations_user_id_users",
        "conversations",
        type_="foreignkey"
    )

    # Remove ownership index.

    op.drop_index(
        "ix_conversations_user_id",
        table_name="conversations"
    )

    # Remove user_id column.

    op.drop_column(
        "conversations",
        "user_id"
    )

    # Remove email index.

    op.drop_index(
        "ix_users_email",
        table_name="users"
    )

    # Remove users table.

    op.drop_table("users")