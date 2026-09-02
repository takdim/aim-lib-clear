"""allow offline submissions

Revision ID: b8e1f2a3c4d5
Revises: a7d9c3e4f6b8
Create Date: 2026-09-02
"""
from alembic import op
import sqlalchemy as sa


revision = 'b8e1f2a3c4d5'
down_revision = 'a7d9c3e4f6b8'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('bebas_pustaka', 'user_id', existing_type=sa.Integer(), nullable=True)


def downgrade():
    op.alter_column('bebas_pustaka', 'user_id', existing_type=sa.Integer(), nullable=False)