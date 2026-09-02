"""add submission creator

Revision ID: a7d9c3e4f6b8
Revises: f1c4d8a9b2e7
Create Date: 2026-09-02
"""
from alembic import op
import sqlalchemy as sa


revision = 'a7d9c3e4f6b8'
down_revision = 'f1c4d8a9b2e7'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('bebas_pustaka', sa.Column('created_by', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_bebas_pustaka_created_by_users',
        'bebas_pustaka', 'users', ['created_by'], ['id']
    )


def downgrade():
    op.drop_constraint('fk_bebas_pustaka_created_by_users', 'bebas_pustaka', type_='foreignkey')
    op.drop_column('bebas_pustaka', 'created_by')