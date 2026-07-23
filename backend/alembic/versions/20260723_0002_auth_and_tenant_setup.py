"""Repair authentication and institution setup tables.

Revision ID: 20260723_0002
Revises: 20260717_0001
Create Date: 2026-07-23
"""

from alembic import op
import sqlalchemy as sa

revision = "20260723_0002"
down_revision = "20260717_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("users"):
        op.create_table(
            "users",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("college_id", sa.String(64), nullable=False),
            sa.Column("username", sa.String(80), nullable=False),
            sa.Column("email", sa.String(255), nullable=False),
            sa.Column("full_name", sa.String(180), nullable=False),
            sa.Column("hashed_password", sa.String(255), nullable=False),
            sa.Column("role", sa.String(80), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint("college_id", "username", name="uq_user_username_per_college"),
            sa.UniqueConstraint("email", name="uq_user_email"),
        )
        op.create_index("ix_users_college_id", "users", ["college_id"])
        op.create_index("ix_users_username", "users", ["username"])
        op.create_index("ix_users_email", "users", ["email"])
        op.create_index("ix_users_college_role", "users", ["college_id", "role"])

    inspector = sa.inspect(bind)
    if not inspector.has_table("refresh_tokens"):
        op.create_table(
            "refresh_tokens",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"])
        op.create_index("ix_refresh_tokens_token_hash", "refresh_tokens", ["token_hash"], unique=True)
        op.create_index("ix_refresh_tokens_user_expires", "refresh_tokens", ["user_id", "expires_at"])

    inspector = sa.inspect(bind)
    if not inspector.has_table("tenant_settings"):
        op.create_table(
            "tenant_settings",
            sa.Column("college_id", sa.String(64), primary_key=True),
            sa.Column("institution_name", sa.String(180), nullable=False),
            sa.Column("campus_name", sa.String(180), nullable=False, server_default=""),
            sa.Column("principal_name", sa.String(180), nullable=False, server_default=""),
            sa.Column("address", sa.String(500), nullable=False, server_default=""),
            sa.Column("phone", sa.String(40), nullable=False, server_default=""),
            sa.Column("email", sa.String(255), nullable=False, server_default=""),
            sa.Column("website", sa.String(255), nullable=False, server_default=""),
            sa.Column("academic_year", sa.String(40), nullable=False, server_default=""),
            sa.Column("timezone", sa.String(64), nullable=False, server_default="Asia/Karachi"),
            sa.Column("currency", sa.String(8), nullable=False, server_default="PKR"),
            sa.Column("logo_url", sa.String(500), nullable=False, server_default=""),
            sa.Column("primary_color", sa.String(16), nullable=False, server_default="#1F4E79"),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )


def downgrade() -> None:
    # The baseline migration historically creates tables dynamically from current
    # metadata. We cannot know whether this repair revision or the baseline owns an
    # existing table, so a destructive downgrade would risk deleting user data.
    # Rollbacks are therefore intentionally data-preserving.
    pass
