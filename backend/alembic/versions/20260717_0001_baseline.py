"""Create the initial College ERP schema.

Revision ID: 20260717_0001
Revises:
Create Date: 2026-07-17
"""

from alembic import op

import app.db.models  # noqa: F401
from app.db.base import Base

revision = "20260717_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all tables for a fresh installation from canonical metadata."""
    Base.metadata.create_all(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    """Drop all application tables when explicitly rolling back the baseline."""
    Base.metadata.drop_all(bind=op.get_bind(), checkfirst=True)
