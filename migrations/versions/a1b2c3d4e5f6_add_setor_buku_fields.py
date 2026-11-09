"""add setor buku fields

Revision ID: a1b2c3d4e5f6
Revises: d4e5f6a7b8c9
Create Date: 2026-09-22
"""
from alembic import op
import sqlalchemy as sa


revision = 'a1b2c3d4e5f6'
down_revision = 'd4e5f6a7b8c9'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'fakultas_setting',
        sa.Column('setor_buku_wajib', sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column('fakultas_setting', 'setor_buku_wajib', server_default=None)

    op.add_column(
        'bebas_pustaka',
        sa.Column('judul_buku_setor', sa.String(length=255), nullable=True),
    )


def downgrade():
    op.drop_column('bebas_pustaka', 'judul_buku_setor')
    op.drop_column('fakultas_setting', 'setor_buku_wajib')
