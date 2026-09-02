"""add fakultas settings

Revision ID: c9d2e4f5a6b7
Revises: b8e1f2a3c4d5
Create Date: 2026-09-02
"""
from alembic import op
import sqlalchemy as sa


revision = 'c9d2e4f5a6b7'
down_revision = 'b8e1f2a3c4d5'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'fakultas_setting',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('fakultas_id', sa.Integer(), nullable=False),
        sa.Column('nama_perpustakaan', sa.String(length=200), nullable=False),
        sa.Column('nomor_urut', sa.Integer(), nullable=False),
        sa.Column('nomor_bagian_tengah', sa.String(length=100), nullable=False),
        sa.Column('nomor_tahun', sa.Integer(), nullable=False),
        sa.Column('pejabat_jabatan', sa.String(length=200), nullable=False),
        sa.Column('pejabat_nama', sa.String(length=150), nullable=False),
        sa.Column('pejabat_nip', sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(['fakultas_id'], ['fakultas.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('fakultas_id'),
    )


def downgrade():
    op.drop_table('fakultas_setting')