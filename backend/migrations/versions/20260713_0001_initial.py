"""initial schema

Revision ID: 20260713_0001
Revises:
Create Date: 2026-07-13
"""
from alembic import op
import sqlalchemy as sa

revision = "20260713_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("permissions", sa.Column("id", sa.String(36), primary_key=True), sa.Column("name", sa.String(120), nullable=False, unique=True), sa.Column("description", sa.String(255)))
    op.create_table("roles", sa.Column("id", sa.String(36), primary_key=True), sa.Column("college_id", sa.String(64), nullable=False), sa.Column("name", sa.String(80), nullable=False), sa.Column("description", sa.String(255)), sa.UniqueConstraint("college_id", "name", name="uq_roles_college_name"))
    op.create_table("users", sa.Column("id", sa.String(36), primary_key=True), sa.Column("college_id", sa.String(64), nullable=False), sa.Column("email", sa.String(255), nullable=False, unique=True), sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False), sa.Column("failed_login_attempts", sa.Integer(), nullable=False), sa.Column("locked_until", sa.DateTime(timezone=True)), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("role_permissions", sa.Column("role_id", sa.String(36), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True), sa.Column("permission_id", sa.String(36), sa.ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True))
    op.create_table("user_roles", sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True), sa.Column("role_id", sa.String(36), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True))
    op.create_table("audit_logs", sa.Column("id", sa.String(36), primary_key=True), sa.Column("user_id", sa.String(36)), sa.Column("action", sa.String(120), nullable=False), sa.Column("resource", sa.String(255)), sa.Column("request_id", sa.String(64)), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))


def downgrade() -> None:
    for table in ("audit_logs", "user_roles", "role_permissions", "users", "roles", "permissions"):
        op.drop_table(table)
