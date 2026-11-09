"""add explicit clearance expiry date

Revision ID: d4e5f6a7b8c9
Revises: c9d2e4f5a6b7
Create Date: 2026-09-02
"""
from alembic import op
import sqlalchemy as sa


revision = 'd4e5f6a7b8c9'
down_revision = 'c9d2e4f5a6b7'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('bebas_pustaka', sa.Column('berlaku_sampai', sa.DateTime(), nullable=True))
    op.execute(
        "UPDATE bebas_pustaka SET berlaku_sampai = DATE_ADD(approved_at, INTERVAL 90 DAY) "
        "WHERE approved_at IS NOT NULL"
    )


def downgrade():
    op.drop_column('bebas_pustaka', 'berlaku_sampai')