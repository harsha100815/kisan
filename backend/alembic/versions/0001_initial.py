"""users + diagnoses audit table

Revision ID: 0001_initial
Revises:
Create Date: 2026-08-25
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON, UUID

from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("phone", sa.String(20), nullable=False),
        sa.Column("name", sa.String(120), nullable=True),
        sa.Column("preferred_language", sa.String(10), nullable=False, server_default="hi"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_users_phone", "users", ["phone"], unique=True)

    op.create_table(
        "diagnoses",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("crop_key", sa.String(50), nullable=True),
        sa.Column("image_ref", sa.String(500), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("predicted_disease_key", sa.String(100), nullable=True),
        sa.Column("confidence", sa.Float, nullable=True),
        sa.Column("confidence_band", sa.String(10), nullable=True),
        sa.Column("is_definitive", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("alternatives", JSON, nullable=True),
        sa.Column("provider", sa.String(30), nullable=False),
        sa.Column("model_version", sa.String(100), nullable=True),
        sa.Column("latency_ms", sa.Integer, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("raw_response", JSON, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_diagnoses_user_id", "diagnoses", ["user_id"])
    op.create_index("ix_diagnoses_created_at", "diagnoses", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_diagnoses_created_at", table_name="diagnoses")
    op.drop_index("ix_diagnoses_user_id", table_name="diagnoses")
    op.drop_table("diagnoses")
    op.drop_index("ix_users_phone", table_name="users")
    op.drop_table("users")
