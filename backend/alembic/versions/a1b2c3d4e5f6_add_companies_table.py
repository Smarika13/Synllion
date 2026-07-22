"""add companies table

Revision ID: a1b2c3d4e5f6
Revises: 0001_initial_schema
Create Date: 2026-07-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '0001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'companies',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=False),
        sa.Column('registration_number', sa.String(length=100), nullable=True),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('website', sa.String(length=500), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('contact_person', sa.String(length=255), nullable=True),
        sa.Column('contact_phone', sa.String(length=20), nullable=True),
        sa.Column('approval_status', sa.String(length=20), nullable=False),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('must_change_password', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], name='companies_reviewed_by_fkey'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='companies_user_id_fkey', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='companies_pkey'),
        sa.UniqueConstraint('user_id', name='companies_user_id_key'),
    )


def downgrade() -> None:
    op.drop_table('companies')