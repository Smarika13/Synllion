"""Create the initial Synllion schema.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-07-15
"""

from alembic import op

from app.db.database import Base
import app.db.models  # noqa: F401  Ensure model tables are registered.

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())
