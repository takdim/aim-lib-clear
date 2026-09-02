"""add tipe pengajuan

Revision ID: f1c4d8a9b2e7
Revises: e34ae49f2a48
Create Date: 2026-09-02
"""
from alembic import op
import sqlalchemy as sa


revision = 'f1c4d8a9b2e7'
down_revision = 'e34ae49f2a48'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'bebas_pustaka',
        sa.Column('tipe_pengajuan', sa.String(length=20), nullable=False, server_default='pusat')
    )
    op.alter_column('bebas_pustaka', 'tipe_pengajuan', server_default=None)


def downgrade():
    op.drop_column('bebas_pustaka', 'tipe_pengajuan')